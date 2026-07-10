from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .models import AttackAction, AttackMode, DefenseAction, LinkName
from .ml_policy import (
    DEFAULT_POLICY_CONFIG_PATH,
    DEFAULT_SKLEARN_MODEL_PATH,
    LogisticRiskModel,
    load_model,
    load_policy_config,
    load_sklearn_model,
    state_to_features,
)


@dataclass
class MissionState:
    tick: int
    active_link: LinkName
    satcom_health: float
    radio_health: float
    lte_health: float
    mesh_health: float
    queue_depth: int
    critical_queue_depth: int
    stale_ratio_window: float
    critical_latency_window: float
    priority_inversion_window: float
    terminal_risk_window: float
    source_trust_drop_window: float
    pace_instability_window: float
    current_attack: AttackMode
    defense_alerted: bool


@dataclass
class AURALite:
    """Safe red-team agent that selects abstract COAs, not real exploits."""

    scenario: AttackMode
    attack_start: int = 35
    pulse_width: int = 30
    cycle_width: int = 42
    max_pulses: int = 3

    def choose_action(self, state: MissionState) -> AttackAction:
        action, _ = self.choose_action_with_candidates(state)
        return action

    def choose_action_with_candidates(
        self,
        state: MissionState,
    ) -> tuple[AttackAction, list[dict[str, Any]]]:
        candidates = self.rank_candidates(state)
        selected = next(candidate for candidate in candidates if candidate["selected"])
        mode = AttackMode(selected["action"])
        target = LinkName(selected["target_link"])
        return AttackAction(
            mode=mode,
            target_link=target,
            intensity=selected["intensity"],
            duration=selected["duration"],
            rationale=selected["reason"],
        ), candidates

    def rank_candidates(self, state: MissionState) -> list[dict[str, Any]]:
        active, phase, window_reason = self._attack_window(state)
        candidates = [self._candidate(AttackMode.NONE, LinkName.SATCOM, 0.0, 0, True, 0.0, window_reason, state)]

        for mode in [AttackMode.LINK_DEGRADATION, AttackMode.MISSION_AWARE_DELAY, AttackMode.FAILOVER_CHASING]:
            eligible = active and self._scenario_allows(mode)
            target = self._target_for(mode, state)
            intensity = self._intensity_for(mode, state)
            score = self._score_candidate(mode, phase, state) if eligible else -1.0
            candidates.append(
                self._candidate(
                    mode,
                    target,
                    intensity,
                    30 if eligible else 0,
                    eligible,
                    score,
                    self._rationale(mode, target, state) if eligible else window_reason,
                    state,
                )
            )

        no_op_score = 1.0 if not active else 0.02
        candidates[0]["score"] = round(no_op_score, 4)
        selected_index = max(range(len(candidates)), key=lambda index: candidates[index]["score"])
        for index, candidate in enumerate(candidates):
            candidate["selected"] = index == selected_index
        return candidates

    def _attack_window(self, state: MissionState) -> tuple[bool, int, str]:
        if self.scenario == AttackMode.NONE:
            return False, 0, "baseline"
        if state.tick < self.attack_start:
            return False, 0, "pre-attack observation window"

        phase = (state.tick - self.attack_start) // self.cycle_width
        if phase >= self.max_pulses:
            return False, phase, "end of exercise"

        offset = (state.tick - self.attack_start) % self.cycle_width
        if offset >= self.pulse_width:
            return False, phase, "cooldown"
        return True, phase, "active bounded attack window"

    def _scenario_allows(self, mode: AttackMode) -> bool:
        return self.scenario == AttackMode.HYBRID or self.scenario == mode

    @staticmethod
    def _target_for(mode: AttackMode, state: MissionState) -> LinkName:
        if mode == AttackMode.FAILOVER_CHASING and state.active_link != LinkName.SATCOM:
            return state.active_link
        return LinkName.SATCOM

    @staticmethod
    def _intensity_for(mode: AttackMode, state: MissionState) -> float:
        if mode == AttackMode.MISSION_AWARE_DELAY and state.critical_queue_depth > 3:
            return 0.46
        if mode == AttackMode.FAILOVER_CHASING:
            return 0.42
        return 0.34

    def _score_candidate(self, mode: AttackMode, phase: int, state: MissionState) -> float:
        preferred = self._hybrid_mode(state) if self.scenario == AttackMode.HYBRID else self.scenario
        phase_bias = 0.72 if mode == preferred else 0.25
        queue_pressure = min(1.0, (state.queue_depth + 2 * state.critical_queue_depth) / 12.0)
        stale_pressure = min(1.0, state.stale_ratio_window / 0.35)
        link_pressure = max(0.0, 1.0 - state.satcom_health)
        pace_pressure = 1.0 if state.active_link != LinkName.SATCOM else state.pace_instability_window

        if mode == AttackMode.LINK_DEGRADATION:
            score = phase_bias + 0.08 * (1.0 - link_pressure) + 0.03 * (1.0 if phase == 0 else 0.0)
        elif mode == AttackMode.MISSION_AWARE_DELAY:
            score = phase_bias + 0.07 * queue_pressure + 0.05 * stale_pressure
        else:
            score = phase_bias + 0.08 * pace_pressure + 0.03 * min(1.0, phase / max(1, self.max_pulses - 1))
        return round(score, 4)

    @staticmethod
    def _candidate(
        mode: AttackMode,
        target: LinkName,
        intensity: float,
        duration: int,
        eligible: bool,
        score: float,
        reason: str,
        state: MissionState,
    ) -> dict[str, Any]:
        return {
            "action": mode.value,
            "target_link": target.value,
            "intensity": round(intensity, 4),
            "duration": duration,
            "eligible": eligible,
            "score": round(score, 4),
            "predicted_effect": {
                "queue_pressure": round(min(1.0, (state.queue_depth + 2 * state.critical_queue_depth) / 12.0), 4),
                "satcom_health": round(state.satcom_health, 4),
                "pace_instability": round(state.pace_instability_window, 4),
            },
            "reason": reason,
            "selected": False,
        }

    def _hybrid_mode(self, state: MissionState) -> AttackMode:
        phase = (state.tick - self.attack_start) // self.cycle_width
        if phase <= 0:
            return AttackMode.LINK_DEGRADATION
        if phase == 1:
            return AttackMode.MISSION_AWARE_DELAY
        return AttackMode.FAILOVER_CHASING

    @staticmethod
    def _rationale(mode: AttackMode, target: LinkName, state: MissionState) -> str:
        if mode == AttackMode.LINK_DEGRADATION:
            return f"degrade {target.value} enough to raise jitter/loss without full outage"
        if mode == AttackMode.MISSION_AWARE_DELAY:
            return "increase mission impact by delaying critical traffic during queue pressure"
        if mode == AttackMode.FAILOVER_CHASING:
            return f"follow defender failover path and reduce recovery stability on {target.value}"
        return "no attack"


@dataclass
class TSRARLite:
    """Blue-team agent for anomaly detection, freshness protection, and PACE routing."""

    detection_threshold: float = 0.58
    stale_threshold: float = 0.25
    critical_latency_threshold: float = 7.0
    alert_tick: int | None = None
    recovery_tick: int | None = None
    health_history: deque[float] = field(default_factory=lambda: deque(maxlen=10))
    stable_ticks: int = 0
    satcom_return_health_threshold: float = 0.86
    satcom_return_risk_threshold: float = 0.50

    def choose_action(self, state: MissionState) -> DefenseAction:
        self.health_history.append(state.satcom_health)
        risk_score = self._risk_score(state)
        degraded = state.satcom_health < self.detection_threshold
        stale_pressure = state.stale_ratio_window > self.stale_threshold
        critical_delay = state.critical_latency_window > self.critical_latency_threshold
        traffic_manipulation = state.priority_inversion_window > 0.05
        access_pressure = state.terminal_risk_window > 0.35 or state.source_trust_drop_window > 0.25

        alert = None
        if risk_score >= 0.42 or degraded or stale_pressure or critical_delay:
            if self.alert_tick is None:
                self.alert_tick = state.tick
            alert = self._build_alert(
                degraded,
                stale_pressure,
                critical_delay,
                traffic_manipulation,
                access_pressure,
            )

        active_link = state.active_link
        satcom_recovered = (
            state.satcom_health >= self.satcom_return_health_threshold
            and risk_score < self.satcom_return_risk_threshold
            and state.critical_latency_window <= 6.0
        )
        if satcom_recovered:
            active_link = LinkName.SATCOM
        elif degraded or risk_score >= 0.55:
            active_link = self._best_pace_link(state)

        backup_link_pressure = active_link != LinkName.SATCOM and (
            state.queue_depth > 1 or state.critical_queue_depth > 0
        )
        deadline_pressure = state.critical_latency_window >= 6.0 or state.priority_inversion_window > 0.0
        minimum_mode = (
            risk_score >= 0.68
            or backup_link_pressure
            or deadline_pressure
            or (degraded and (stale_pressure or critical_delay))
        )
        priority_boost = (
            risk_score >= 0.45
            or degraded
            or critical_delay
            or state.critical_queue_depth > 0
            or (state.queue_depth > 4 and state.satcom_health < 0.92)
        )
        quarantine = risk_score >= 0.72 or access_pressure
        pace_transition = active_link != state.active_link

        if self.alert_tick is not None and self.recovery_tick is None:
            recovered_path = (
                state.queue_depth < 10
                and state.critical_latency_window <= 7.0
                and state.stale_ratio_window <= self.stale_threshold
            )
            recovered = (
                risk_score < 0.36
                and state.queue_depth < 10
                and state.critical_latency_window <= 7.0
            ) or recovered_path
            if recovered:
                self.stable_ticks += 1
                if self.stable_ticks >= 4:
                    self.recovery_tick = state.tick
            else:
                self.stable_ticks = 0

        return DefenseAction(
            active_link=active_link,
            priority_boost=priority_boost,
            minimum_mode=minimum_mode,
            alert=alert,
            stale_badge=stale_pressure,
            risk_score=round(risk_score, 4),
            quarantine=quarantine,
            pace_transition=pace_transition,
            decision_basis={
                "policy_kind": "heuristic_risk_fusion",
                "heuristic_risk": round(risk_score, 4),
                "fused_risk": round(risk_score, 4),
                "degraded": degraded,
                "stale_pressure": stale_pressure,
                "critical_delay": critical_delay,
                "traffic_manipulation": traffic_manipulation,
                "access_pressure": access_pressure,
            },
        )

    @staticmethod
    def _best_pace_link(state: MissionState) -> LinkName:
        link_scores = {
            LinkName.RADIO: state.radio_health * 180,
            LinkName.LTE: state.lte_health * 420,
            LinkName.MESH: state.mesh_health * 260,
        }
        return max(link_scores, key=link_scores.get)

    @staticmethod
    def _risk_score(state: MissionState) -> float:
        link_degradation = max(0.0, 1.0 - state.satcom_health)
        stale = min(1.0, state.stale_ratio_window / 0.35)
        critical = min(1.0, state.critical_latency_window / 12.0)
        source = min(1.0, state.source_trust_drop_window)
        priority = min(1.0, state.priority_inversion_window / 0.25)
        terminal = min(1.0, state.terminal_risk_window)
        pace = min(1.0, state.pace_instability_window)
        return min(
            1.0,
            0.20 * link_degradation
            + 0.20 * stale
            + 0.20 * critical
            + 0.15 * source
            + 0.10 * priority
            + 0.10 * terminal
            + 0.05 * pace,
        )

    @staticmethod
    def _build_alert(
        degraded: bool,
        stale_pressure: bool,
        critical_delay: bool,
        traffic_manipulation: bool,
        access_pressure: bool,
    ) -> str:
        reasons = []
        if degraded:
            reasons.append("link degradation")
        if stale_pressure:
            reasons.append("COP stale pressure")
        if critical_delay:
            reasons.append("critical latency")
        if traffic_manipulation:
            reasons.append("priority inversion")
        if access_pressure:
            reasons.append("terminal/source trust pressure")
        if not reasons:
            reasons.append("fused mission-risk anomaly")
        return "TSRA-R alert: " + ", ".join(reasons)


@dataclass
class MLTSRARLite(TSRARLite):
    """TSRA-R variant backed by a trained logistic risk classifier."""

    model: LogisticRiskModel = field(default_factory=load_model)
    sklearn_model: object | None = field(default_factory=lambda: load_sklearn_model() if DEFAULT_SKLEARN_MODEL_PATH.exists() else None)
    policy_config: dict[str, float] = field(default_factory=lambda: load_policy_config() if DEFAULT_POLICY_CONFIG_PATH.exists() else {})
    ml_alert_threshold: float = 0.50
    ml_priority_threshold: float = 0.42
    ml_minimum_mode_threshold: float = 0.72
    ml_pace_threshold: float = 0.50
    ml_stale_badge_threshold: float = 0.62
    ml_quarantine_threshold: float = 0.78
    ml_recovery_threshold: float = 0.32
    ml_weight: float = 0.65
    heuristic_weight: float = 0.35
    recovery_stable_ticks_required: int = 3
    recovery_queue_threshold: int = 12
    recovery_latency_threshold: float = 6.0
    critical_queue_guard_threshold: int = 0
    queue_guard_threshold: int = 4
    satcom_guard_threshold: float = 0.92
    backup_link_queue_threshold: int = 1

    def __post_init__(self) -> None:
        for key, value in self.policy_config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def choose_action(self, state: MissionState) -> DefenseAction:
        features = state_to_features(state)
        ml_risk = self._predict_ml_risk(features)
        heuristic_risk = self._risk_score(state)
        fused_risk = min(1.0, self.ml_weight * ml_risk + self.heuristic_weight * heuristic_risk)
        model_backend = "sklearn_ensemble" if self.sklearn_model is not None else "logistic_fallback"

        degraded = state.satcom_health < self.detection_threshold
        stale_pressure = state.stale_ratio_window > self.stale_threshold
        critical_delay = state.critical_latency_window > self.critical_latency_threshold
        traffic_manipulation = state.priority_inversion_window > 0.03
        access_pressure = state.terminal_risk_window > 0.30 or state.source_trust_drop_window > 0.22

        alert = None
        if fused_risk >= self.ml_alert_threshold or degraded or stale_pressure or critical_delay:
            if self.alert_tick is None:
                self.alert_tick = state.tick
            alert = self._build_alert(
                degraded,
                stale_pressure,
                critical_delay,
                traffic_manipulation,
                access_pressure,
            )

        active_link = state.active_link
        satcom_recovered = (
            state.satcom_health >= self.satcom_return_health_threshold
            and fused_risk < max(0.34, self.satcom_return_risk_threshold)
            and state.critical_latency_window <= self.recovery_latency_threshold
        )
        if satcom_recovered:
            active_link = LinkName.SATCOM
        elif degraded or fused_risk >= self.ml_pace_threshold:
            active_link = self._best_pace_link(state)

        backup_link_pressure = (
            active_link != LinkName.SATCOM
            and (
                state.queue_depth > self.backup_link_queue_threshold
                or state.critical_queue_depth > self.critical_queue_guard_threshold
            )
        )
        deadline_pressure = (
            state.critical_latency_window >= self.recovery_latency_threshold
            or state.priority_inversion_window > 0.0
        )
        priority_boost = (
            fused_risk >= self.ml_priority_threshold
            or degraded
            or critical_delay
            or traffic_manipulation
            or (
                state.critical_queue_depth > self.critical_queue_guard_threshold
                and (
                    state.queue_depth > self.queue_guard_threshold
                    or state.satcom_health < self.satcom_guard_threshold
                )
            )
        )
        minimum_mode = (
            fused_risk >= self.ml_minimum_mode_threshold
            or backup_link_pressure
            or deadline_pressure
            or (degraded and (stale_pressure or critical_delay))
        )
        quarantine = fused_risk >= self.ml_quarantine_threshold or access_pressure
        pace_transition = active_link != state.active_link

        if self.alert_tick is not None and self.recovery_tick is None:
            recovered_path = (
                state.queue_depth < self.recovery_queue_threshold
                and state.critical_latency_window <= self.recovery_latency_threshold
                and state.stale_ratio_window <= self.stale_threshold
            )
            recovered = (
                (
                    fused_risk < self.ml_recovery_threshold
                    and state.queue_depth < self.recovery_queue_threshold
                    and state.critical_latency_window <= self.recovery_latency_threshold
                )
                or recovered_path
            )
            if recovered:
                self.stable_ticks += 1
                if self.stable_ticks >= self.recovery_stable_ticks_required:
                    self.recovery_tick = state.tick
            else:
                self.stable_ticks = 0

        return DefenseAction(
            active_link=active_link,
            priority_boost=priority_boost,
            minimum_mode=minimum_mode,
            alert=alert,
            stale_badge=stale_pressure or ml_risk >= self.ml_stale_badge_threshold,
            risk_score=round(fused_risk, 4),
            quarantine=quarantine,
            pace_transition=pace_transition,
            decision_basis={
                "policy_kind": "ml_risk_fusion",
                "model_backend": model_backend,
                "ml_risk": round(ml_risk, 4),
                "heuristic_risk": round(heuristic_risk, 4),
                "fused_risk": round(fused_risk, 4),
                "ml_weight": round(self.ml_weight, 4),
                "heuristic_weight": round(self.heuristic_weight, 4),
                "feature_count": len(features),
                "ml_alert_threshold": self.ml_alert_threshold,
                "ml_priority_threshold": self.ml_priority_threshold,
                "ml_minimum_mode_threshold": self.ml_minimum_mode_threshold,
                "ml_pace_threshold": self.ml_pace_threshold,
                "degraded": degraded,
                "stale_pressure": stale_pressure,
                "critical_delay": critical_delay,
                "traffic_manipulation": traffic_manipulation,
                "access_pressure": access_pressure,
            },
        )

    def _predict_ml_risk(self, features: list[float]) -> float:
        if self.sklearn_model is not None:
            probability = self.sklearn_model.predict_proba([features])[0][1]
            return float(probability)
        return self.model.predict_probability(features)

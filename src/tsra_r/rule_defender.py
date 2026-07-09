from __future__ import annotations

from src.shared.schemas import DefenseEvent, MissionState


class RuleTSRAR:
    def __init__(self, mode: str = "full") -> None:
        self.mode = mode
        self.action_cooldowns: dict[str, float] = {}
        self.event_count = 0

    def _ready(self, action: str, now: float, cooldown: float) -> bool:
        last = self.action_cooldowns.get(action, -10_000.0)
        return now - last >= cooldown

    def _event(self, state: MissionState, action: str, details: dict) -> DefenseEvent:
        self.event_count += 1
        self.action_cooldowns[action] = state.time_sec
        return DefenseEvent(
            event_id=f"def-{self.event_count:05d}",
            time_sec=state.time_sec,
            action=action,
            details=details,
        )

    def decide(self, state: MissionState) -> list[DefenseEvent]:
        events: list[DefenseEvent] = []
        now = state.time_sec

        if (
            state.critical_pending > 0
            and state.video_queue_kb > 500
            and self._ready("priority_reroute", now, 25)
        ):
            events.append(
                self._event(
                    state,
                    "priority_reroute",
                    {"until_sec": now + 70, "reason": "critical traffic waiting behind video load"},
                )
            )

        if state.video_queue_kb > 1500 and self._ready("video_throttle", now, 35):
            events.append(
                self._event(
                    state,
                    "video_throttle",
                    {"until_sec": now + 60, "reason": "protect critical traffic capacity"},
                )
            )

        if state.stale_data_ratio > 0.25 and self._ready("stale_badge", now, 30):
            events.append(
                self._event(
                    state,
                    "stale_badge",
                    {"until_sec": now + 90, "stale_ratio": state.stale_data_ratio},
                )
            )

        if self.mode != "full":
            return events

        active = state.links[state.active_link]
        satcom_bad = (
            state.active_link == "SATCOM"
            and (
                active.base_latency_ms > 1100
                or active.loss_rate > 0.055
                or state.total_queue_kb > 4500
            )
        )
        if satcom_bad and self._ready("pace_switch", now, 80):
            target = self._best_fallback_link(state)
            if target:
                events.append(
                    self._event(
                        state,
                        "pace_switch",
                        {
                            "target_link": target,
                            "until_sec": now + 100,
                            "move_critical": True,
                            "reason": "SATCOM degraded beyond mission threshold",
                        },
                    )
                )

        return events

    @staticmethod
    def _best_fallback_link(state: MissionState) -> str | None:
        candidates = []
        for name, link in state.links.items():
            if name == "SATCOM" or not link.available:
                continue
            score = link.bandwidth_mbps / max(link.base_latency_ms / 1000.0, 0.1)
            score -= 5.0 * link.loss_rate
            candidates.append((score, name))
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]


from datetime import datetime, timedelta


SEVERITY_PRIORITY = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def correlate_events(
    events: list[dict],
    window_seconds: int = 60,
    context_seconds: int = 10
) -> list[dict]:

    # Trier les événements chronologiquement
    sorted_events = sorted(
        events,
        key=lambda event: parse_timestamp(event["timestamp"])
    )

    # Garder les événements qui peuvent déclencher un incident
    triggers = [
        event for event in sorted_events
        if event.get("severity") in ("HIGH", "CRITICAL")
    ]

    if not triggers:
        return []

    # Regrouper les événements déclencheurs proches
    groups = []
    current_group = [triggers[0]]

    for event in triggers[1:]:
        current_time = parse_timestamp(event["timestamp"])
        previous_time = parse_timestamp(
            current_group[-1]["timestamp"]
        )

        difference = (current_time - previous_time).total_seconds()

        if difference <= window_seconds:
            current_group.append(event)
        else:
            groups.append(current_group)
            current_group = [event]

    groups.append(current_group)

    incidents = []

    for index, group in enumerate(groups, start=1):

        first_time = parse_timestamp(group[0]["timestamp"])
        last_time = parse_timestamp(group[-1]["timestamp"])

        # Ajouter les WARNING proches comme contexte
        context_events = [
            event for event in sorted_events
            if event.get("severity") == "MEDIUM"
            and first_time - timedelta(seconds=context_seconds)
            <= parse_timestamp(event["timestamp"])
            <= last_time + timedelta(seconds=context_seconds)
        ]

        # Événement ayant la sévérité la plus élevée
        primary_event = max(
            group,
            key=lambda event: SEVERITY_PRIORITY.get(
                event.get("severity", "LOW"), 0
            )
        )

        all_incident_events = sorted(
            group + context_events,
            key=lambda event: parse_timestamp(event["timestamp"])
        )

        incidents.append({
            "incident_id": f"INC-{index:03d}",
            "title": (
                primary_event["category"].replace("_", " ").title()
                + " Incident"
            ),
            "severity": primary_event["severity"],
            "primary_category": primary_event["category"],
            "first_seen": first_time.isoformat(sep=" "),
            "last_seen": last_time.isoformat(sep=" "),
            "event_count": len(all_incident_events),
            "trigger_count": len(group),
            "events": all_incident_events,
            "correlation_reason": (
                f"{len(group)} high-severity events detected "
                f"within a {window_seconds}-second window."
            )
        })

    return incidents

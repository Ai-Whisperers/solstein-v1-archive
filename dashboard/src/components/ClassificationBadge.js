import { Badge } from "@tremor/react";

export function ClassificationBadge({ classification }) {
    const isRocket = classification === "Rocket";
    const isDino = classification === "Dinosaur";

    const color = isRocket ? "emerald" : isDino ? "rose" : "blue";
    const icon = isRocket ? "🚀" : isDino ? "🦕" : "⚖️";

    return (
        <Badge color={color} size="sm" className="font-semibold tracking-wider uppercase">
            {icon} {classification}
        </Badge>
    );
}

import { Badge } from "@tremor/react";

export function ClassificationBadge({
    classification,
}: {
    classification: string;
}) {
    const isPhoenix = classification === "Phoenix";
    const isLead = classification === "Lead";
    const isSalt = classification === "Salt";

    const className = isPhoenix
        ? "badge-phoenix"
        : isLead
            ? "badge-lead"
            : isSalt
                ? "badge-salt"
                : "";

    const icon = isPhoenix ? "🔥" : isLead ? "⚖️" : "🧂";

    return (
        <span className={`${className} inline-flex items-center gap-1 shadow-lg shadow-black/20`}>
            <span>{icon}</span>
            <span>{classification}</span>
        </span>
    );
}

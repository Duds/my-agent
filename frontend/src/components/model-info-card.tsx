'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Model } from '@/lib/store';
import {
  Globe,
  Server,
  Cpu,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
} from 'lucide-react';

interface ModelInfoCardProps {
  model: Model;
  /** Compact: tags + benefits only. Full: pros, cons, benefits */
  variant?: 'compact' | 'full';
  className?: string;
}

function getTypeIcon(type: Model['type'] | undefined) {
  switch (type) {
    case 'commercial':
      return <Globe className="h-3.5 w-3.5 text-primary" />;
    case 'ollama':
      return <Server className="h-3.5 w-3.5 text-emerald-600" />;
    case 'local':
      return <Cpu className="h-3.5 w-3.5 text-amber-600" />;
    default:
      return <Server className="h-3.5 w-3.5 text-muted-foreground" />;
  }
}

export function ModelInfoCard({
  model,
  variant = 'full',
  className,
}: ModelInfoCardProps) {
  const tags = model.tags ?? [];
  const pros = model.pros ?? [];
  const cons = model.cons ?? [];
  const benefits = model.benefits ?? '';

  return (
    <div
      className={cn(
        'rounded-md border bg-popover p-3 text-popover-foreground shadow-md',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-2">
        <div className="mt-0.5 shrink-0">{getTypeIcon(model.type)}</div>
        <div className="min-w-0 flex-1">
          <p className="font-medium text-sm">{model.name}</p>
          <p className="text-muted-foreground text-xs">{model.provider}</p>
          {model.contextWindow && (
            <p className="text-muted-foreground mt-0.5 text-[10px]">
              Context: {model.contextWindow}
            </p>
          )}
        </div>
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {tags.map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className="text-[10px] font-normal px-1.5 py-0"
            >
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Benefits summary */}
      {benefits && (
        <div className="mt-2 flex gap-2">
          <Sparkles className="h-3.5 w-3.5 shrink-0 text-primary mt-0.5" />
          <p className="text-xs leading-relaxed text-muted-foreground">
            {benefits}
          </p>
        </div>
      )}

      {/* Pros & Cons (full variant) */}
      {variant === 'full' && (pros.length > 0 || cons.length > 0) && (
        <div className="mt-3 space-y-2 border-t pt-3">
          {pros.length > 0 && (
            <div>
              <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                <ThumbsUp className="h-3 w-3" />
                Pros
              </p>
              <ul className="mt-1 space-y-0.5">
                {pros.map((p, i) => (
                  <li
                    key={i}
                    className="text-[11px] leading-relaxed text-muted-foreground pl-4"
                  >
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {cons.length > 0 && (
            <div>
              <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                <ThumbsDown className="h-3 w-3" />
                Cons
              </p>
              <ul className="mt-1 space-y-0.5">
                {cons.map((c, i) => (
                  <li
                    key={i}
                    className="text-[11px] leading-relaxed text-muted-foreground pl-4"
                  >
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

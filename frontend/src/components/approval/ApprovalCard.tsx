'use client';

import React, { useState } from 'react';
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from 'framer-motion';
import { Check, X, RotateCcw, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export type ApprovalItem = {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  reasoning?: string;
  metadata?: Record<string, string>;
  type: 'file' | 'automation' | 'security' | 'other';
};

interface ApprovalCardProps {
  item: ApprovalItem;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  className?: string;
}

export const ApprovalCard: React.FC<ApprovalCardProps> = ({
  item,
  onApprove,
  onReject,
  className,
}) => {
  const [exitDirection, setExitDirection] = useState<number>(0);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-25, 25]);
  const opacity = useTransform(x, [-200, -150, 0, 150, 200], [0, 1, 1, 1, 0]);
  const approveOpacity = useTransform(x, [50, 150], [0, 1]);
  const rejectOpacity = useTransform(x, [-150, -50], [1, 0]);

  const handleDragEnd = (_: any, info: any) => {
    if (info.offset.x > 100) {
      setExitDirection(200);
      onApprove(item.id);
    } else if (info.offset.x < -100) {
      setExitDirection(-200);
      onReject(item.id);
    }
  };

  return (
    <div
      className={cn('relative mx-auto h-[400px] w-full max-w-sm', className)}
    >
      <AnimatePresence>
        <motion.div
          style={{ x, rotate, opacity }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          onDragEnd={handleDragEnd}
          whileTap={{ scale: 0.95 }}
          className="absolute inset-0 z-10 cursor-grab active:cursor-grabbing"
        >
          <Card className="border-primary/20 bg-background/60 flex h-full flex-col overflow-hidden shadow-2xl backdrop-blur-xl">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div className="bg-primary/10 text-primary rounded-lg p-2">
                  {item.type === 'file' && <RotateCcw size={20} />}
                  {item.type === 'automation' && <Check size={20} />}
                  {item.type === 'security' && <Info size={20} />}
                  {item.type === 'other' && <Info size={20} />}
                </div>
                <div className="text-muted-foreground bg-muted rounded px-2 py-1 text-[10px] font-bold tracking-wider uppercase">
                  {item.type}
                </div>
              </div>
              <CardTitle className="mt-4 text-xl leading-tight">
                {item.title}
              </CardTitle>
              {item.subtitle && (
                <p className="text-muted-foreground text-sm">{item.subtitle}</p>
              )}
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto pt-2">
              {item.description && (
                <p className="border-primary/30 mb-4 border-l-2 pl-3 text-sm italic">
                  {item.description}
                </p>
              )}
              {item.reasoning && (
                <div className="bg-secondary/30 border-secondary rounded-lg border p-3">
                  <p className="mb-1 flex items-center gap-1 text-xs font-semibold">
                    <Info size={12} className="text-primary" /> Reasoning
                  </p>
                  <p className="text-muted-foreground text-xs leading-relaxed">
                    {item.reasoning}
                  </p>
                </div>
              )}
              {item.metadata && (
                <div className="mt-4 space-y-1">
                  {Object.entries(item.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-[10px]">
                      <span className="text-muted-foreground font-medium">
                        {key}:
                      </span>
                      <span className="text-primary/80 font-mono">{value}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>

            <CardFooter className="grid grid-cols-2 gap-4 pt-2">
              <Button
                variant="outline"
                className="border-destructive/30 hover:bg-destructive/10 text-destructive w-full"
                onClick={() => onReject(item.id)}
              >
                <X className="mr-2 h-4 w-4" /> Reject
              </Button>
              <Button
                className="shadow-primary/20 w-full shadow-lg"
                onClick={() => onApprove(item.id)}
              >
                <Check className="mr-2 h-4 w-4" /> Approve
              </Button>
            </CardFooter>

            {/* Swipe Indicators */}
            <motion.div
              style={{ opacity: approveOpacity }}
              className="pointer-events-none absolute inset-0 flex items-center justify-center bg-green-500/20"
            >
              <Check size={80} className="text-green-500/50" />
            </motion.div>
            <motion.div
              style={{ opacity: rejectOpacity }}
              className="bg-destructive/20 pointer-events-none absolute inset-0 flex items-center justify-center"
            >
              <X size={80} className="text-destructive/50" />
            </motion.div>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

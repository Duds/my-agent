'use client';

import React, { useState } from 'react';
import { Lock, ShieldAlert, Key } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';
import { api } from '@/lib/api-client';
import { useToast } from '@/components/ui/use-toast';

interface VaultOverlayProps {
  onUnlock: () => void;
  isInitialized: boolean;
}

export function VaultOverlay({ onUnlock, isInitialized }: VaultOverlayProps) {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const handleUnlock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) return;

    setLoading(true);
    setError(null);
    try {
      await api.unlockVault(password);
      toast({
        title: isInitialized ? 'Vault Unlocked' : 'Vault Initialized',
        description: isInitialized
          ? 'You now have access to your secrets.'
          : 'Your master password has been set.',
      });
      onUnlock();
    } catch (err: any) {
      setError(err.message || 'Failed to unlock vault');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background/80 absolute inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <Card className="border-primary/20 w-full max-w-sm shadow-2xl">
        <CardHeader className="text-center">
          <div className="bg-primary/10 text-primary mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
            {isInitialized ? (
              <Lock className="h-6 w-6" />
            ) : (
              <ShieldAlert className="text-warning h-6 w-6" />
            )}
          </div>
          <CardTitle>
            {isInitialized ? 'Vault Locked' : 'Initialize Privacy Vault'}
          </CardTitle>
          <CardDescription>
            {isInitialized
              ? 'Enter your master password to access sensitive data.'
              : 'Set a master password. If lost, your vault data cannot be recovered.'}
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleUnlock}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="relative">
                <Key className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
                <Input
                  type="password"
                  placeholder="Master Password"
                  className="pl-9"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoFocus
                />
              </div>
              {error && (
                <p className="text-destructive mt-1 text-[11px] font-medium">
                  {error}
                </p>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-2">
            <Button
              type="submit"
              className="w-full"
              disabled={loading || !password}
            >
              {loading
                ? 'Processing...'
                : isInitialized
                  ? 'Unlock Vault'
                  : 'Set Password & Initialize'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

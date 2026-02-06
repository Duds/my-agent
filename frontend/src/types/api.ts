/** API response types for the Secure Personal Agentic Platform */

export interface RoutingInfo {
  intent: string;
  adapter: string;
  requires_privacy: boolean;
}

export interface SecurityInfo {
  is_safe: boolean;
  reason: string;
}

export interface QueryResponse {
  status: string;
  routing: RoutingInfo;
  answer: string;
  security?: SecurityInfo;
}

export interface HealthResponse {
  status: string;
  service: string;
}

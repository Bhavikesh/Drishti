export type Role = 'constable' | 'inspector' | 'sp' | 'admin';

export interface User {
  id: number;
  email: string;
  role: Role;
  assigned_district: string | null;
  assigned_station_id: number | null;
}

export interface Crime {
  id: number;
  case_id: string;
  crime_date: string;
  district: string;
  police_station_id: number;
  crime_type: string;
  description: string;
  status: string;
  lat: number;
  lng: number;
  is_resolved: boolean;
  resolution_date: string | null;
}

export interface Criminal {
  id: number;
  name: string;
  age: number;
  gender: string;
  criminal_history_count: number;
  is_repeat_offender: boolean;
  first_offense_date: string;
}

export interface NetworkNode {
  id: string;
  name: string;
  crimeCount: number;
  type?: string;
}

export interface NetworkLink {
  source: string;
  target: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AuditLog {
  id: number;
  user_id: number;
  query: string;
  response: string;
  timestamp: string;
  ip_address: string;
}

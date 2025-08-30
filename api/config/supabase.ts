import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error('Missing Supabase environment variables');
}

// Create Supabase client with service role key for server-side operations
export const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// Database types
export interface User {
  id: string;
  email: string;
  name: string;
  password_hash: string;
  user_type: 'normal' | 'enterprise' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  budget: number;
  deadline: string;
  status: 'draft' | 'active' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface Simulation {
  id: string;
  project_id: string;
  name: string;
  base_price: number;
  competitor_count: number;
  market_conditions: 'stable' | 'competitive' | 'volatile';
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

export interface SimulationResult {
  id: string;
  simulation_id: string;
  recommended_price: number;
  win_probability: number;
  profit_margin: number;
  risk_score: number;
  analysis_data: any;
  created_at: string;
}
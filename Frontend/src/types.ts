export type Screen = 'login' | 'dashboard' | 'result';

export interface CropResult {
  name: string;
  disease: string;
  confidence: number;
  severity: string;
  imageUrl: string;
  actions: string[];
}

export interface RecentScan {
  id: string;
  name: string;
  status: 'HEALTHY' | 'ISSUES FOUND';
  time: string;
  imageUrl: string;
}

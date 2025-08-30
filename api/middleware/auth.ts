import { Request, Response, NextFunction } from 'express';
import { verifyToken, extractTokenFromHeader, JWTPayload } from '../utils/jwt.js';

// Extend Express Request interface to include user
declare global {
  namespace Express {
    interface Request {
      user?: JWTPayload;
    }
  }
}

/**
 * Authentication middleware
 * Verifies JWT token and adds user info to request
 */
export const authenticateToken = (req: Request, res: Response, next: NextFunction): void => {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);
    const user = verifyToken(token);
    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({
      success: false,
      message: 'Authentication failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

/**
 * Authorization middleware for specific user types
 */
export const requireUserType = (allowedTypes: Array<'normal' | 'enterprise' | 'admin'>) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
      return;
    }

    if (!allowedTypes.includes(req.user.userType)) {
      res.status(403).json({
        success: false,
        message: 'Insufficient permissions'
      });
      return;
    }

    next();
  };
};

/**
 * Admin only middleware
 */
export const requireAdmin = requireUserType(['admin']);

/**
 * Enterprise or Admin middleware
 */
export const requireEnterpriseOrAdmin = requireUserType(['enterprise', 'admin']);
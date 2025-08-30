/**
 * User authentication API routes
 * Handle user registration, login, token management, etc.
 */
import { Router, type Request, type Response } from 'express';
import bcrypt from 'bcryptjs';
import { mockDataStore } from '../data/mockData';
import { authenticateToken } from '../middleware/auth.js';
import { generateToken } from '../utils/jwt.js';

const router = Router();

/**
 * User Registration
 * POST /api/auth/register
 */
router.post('/register', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password || !name) {
      res.status(400).json({ 
        success: false, 
        message: 'Email, password and name are required' 
      });
      return;
    }

    // 检查用户是否已存在
    const existingUser = await mockDataStore.getUserByEmail(email);

    if (existingUser) {
      res.status(400).json({ 
        success: false, 
        message: 'User already exists' 
      });
      return;
    }

    // 加密密码
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // 创建用户
    const newUser = await mockDataStore.createUser({
      email,
      password: hashedPassword,
      name
    });

    // 生成JWT token
    const token = generateToken({
      userId: newUser.id,
      email: newUser.email,
      userType: newUser.user_type
    });

    res.status(201).json({
      success: true,
      message: 'User created successfully',
      data: {
        user: {
          id: newUser.id,
          email: newUser.email,
          name: newUser.name,
          user_type: newUser.user_type,
          created_at: newUser.created_at,
          updated_at: newUser.updated_at
        },
        token
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error' 
    });
  }
});

/**
 * User Login
 * POST /api/auth/login
 */
router.post('/login', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ 
        success: false, 
        message: 'Email and password are required' 
      });
      return;
    }

    // 查找用户
    const user = await mockDataStore.getUserByEmail(email);

    if (!user) {
      res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
      return;
    }

    // 验证密码
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
      return;
    }

    // 生成JWT token
    const token = generateToken({
      userId: user.id,
      email: user.email,
      userType: user.user_type
    });

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          user_type: user.user_type,
          created_at: user.created_at,
          updated_at: user.updated_at
        },
        token
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error' 
    });
  }
});

/**
 * Get Current User Profile
 * GET /api/auth/profile
 */
router.get('/profile', authenticateToken, async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user.userId;

    const user = await mockDataStore.getUserById(userId);

    if (!user) {
      res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
      return;
    }

    res.json({
      success: true,
      data: { 
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          created_at: user.created_at
        }
      }
    });
  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error' 
    });
  }
});

/**
 * User Logout
 * POST /api/auth/logout
 */
router.post('/logout', authenticateToken, async (req: Request, res: Response): Promise<void> => {
  // In a stateless JWT system, logout is handled client-side by removing the token
  // For enhanced security, you could implement a token blacklist here
  res.json({
    success: true,
    message: 'Logout successful'
  });
});

export default router;
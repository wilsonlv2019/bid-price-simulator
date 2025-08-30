/**
 * Project management API routes
 * Handle project CRUD operations
 */
import { Router, type Request, type Response } from 'express';
import { mockDataStore } from '../data/mockData.js';
import { authenticateToken } from '../middleware/auth.js';

const router = Router();

// Apply authentication middleware to all routes
router.use(authenticateToken);

/**
 * Get all projects for the authenticated user
 * GET /api/projects
 */
router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = req.user!.userId;

    const projects = await mockDataStore.getProjectsByUserId(userId);

    res.json({
      success: true,
      data: { projects }
    });
  } catch (error) {
    console.error('Get projects error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Get a specific project by ID
 * GET /api/projects/:id
 */
router.get('/:id', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const userId = req.user!.userId;

    const project = await mockDataStore.getProjectById(id);

    if (!project || project.user_id !== userId) {
      res.status(404).json({
        success: false,
        message: 'Project not found'
      });
      return;
    }

    res.json({
      success: true,
      data: { project }
    });
  } catch (error) {
    console.error('Get project error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Create a new project
 * POST /api/projects
 */
router.post('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const { name, description, budget, deadline } = req.body;

    // Validate input
    if (!name || !budget || !deadline) {
      res.status(400).json({
        success: false,
        message: 'Name, budget, and deadline are required'
      });
      return;
    }

    // Validate budget is a positive number
    if (typeof budget !== 'number' || budget <= 0) {
      res.status(400).json({
        success: false,
        message: 'Budget must be a positive number'
      });
      return;
    }

    // Validate deadline is a valid date
    const deadlineDate = new Date(deadline);
    if (isNaN(deadlineDate.getTime())) {
      res.status(400).json({
        success: false,
        message: 'Invalid deadline format'
      });
      return;
    }

    // Check if deadline is in the future
    if (deadlineDate <= new Date()) {
      res.status(400).json({
        success: false,
        message: 'Deadline must be in the future'
      });
      return;
    }

    const project = await mockDataStore.createProject({
      user_id: req.user!.userId,
      name,
      description: description || null,
      budget,
      deadline: deadline,
      status: 'active'
    });

    res.status(201).json({
      success: true,
      message: 'Project created successfully',
      data: { project }
    });
  } catch (error) {
    console.error('Create project error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Update a project
 * PUT /api/projects/:id
 */
router.put('/:id', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { name, description, budget, deadline, status } = req.body;

    // Check if project exists and belongs to user
    const existingProject = await mockDataStore.getProjectById(id);

    if (!existingProject || existingProject.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Project not found'
      });
      return;
    }

    // Prepare update data
    const updateData: any = {};
    
    if (name !== undefined) {
      if (!name.trim()) {
        res.status(400).json({
          success: false,
          message: 'Name cannot be empty'
        });
        return;
      }
      updateData.name = name;
    }

    if (description !== undefined) {
      updateData.description = description;
    }

    if (budget !== undefined) {
      if (typeof budget !== 'number' || budget <= 0) {
        res.status(400).json({
          success: false,
          message: 'Budget must be a positive number'
        });
        return;
      }
      updateData.budget = budget;
    }

    if (deadline !== undefined) {
      const deadlineDate = new Date(deadline);
      if (isNaN(deadlineDate.getTime())) {
        res.status(400).json({
          success: false,
          message: 'Invalid deadline format'
        });
        return;
      }
      updateData.deadline = deadline;
    }

    if (status !== undefined) {
      const validStatuses = ['draft', 'active', 'completed', 'cancelled'];
      if (!validStatuses.includes(status)) {
        res.status(400).json({
          success: false,
          message: 'Invalid status. Must be one of: draft, active, completed, cancelled'
        });
        return;
      }
      updateData.status = status;
    }

    updateData.updated_at = new Date().toISOString();

    const project = await mockDataStore.updateProject(id, updateData);

    if (!project) {
      console.error('Failed to update project');
      res.status(500).json({
        success: false,
        message: 'Failed to update project'
      });
      return;
    }

    res.json({
      success: true,
      message: 'Project updated successfully',
      data: { project }
    });
  } catch (error) {
    console.error('Update project error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Delete a project
 * DELETE /api/projects/:id
 */
router.delete('/:id', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;

    // Check if project exists and belongs to user
    const existingProject = await mockDataStore.getProjectById(id);

    if (!existingProject || existingProject.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Project not found'
      });
      return;
    }

    const success = await mockDataStore.deleteProject(id);

    if (!success) {
      console.error('Failed to delete project');
      res.status(500).json({
        success: false,
        message: 'Failed to delete project'
      });
      return;
    }

    res.json({
      success: true,
      message: 'Project deleted successfully'
    });
  } catch (error) {
    console.error('Delete project error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

export default router;
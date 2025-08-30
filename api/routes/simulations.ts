/**
 * Simulation analysis API routes
 * Handle bidding price simulation and analysis
 */
import { Router, type Request, type Response } from 'express';
import { mockDataStore } from '../data/mockData.js';
import { authenticateToken } from '../middleware/auth.js';

const router = Router();

// Apply authentication middleware to all routes
router.use(authenticateToken);

/**
 * Price simulation algorithm
 * This is a simplified version - in production, this would be more sophisticated
 */
class PriceSimulator {
  /**
   * Calculate recommended bidding price based on various factors
   */
  static calculateRecommendedPrice(params: {
    basePrice: number;
    competitorCount: number;
    marketConditions: 'stable' | 'competitive' | 'volatile';
    riskLevel: 'low' | 'medium' | 'high';
    budget: number;
  }) {
    const { basePrice, competitorCount, marketConditions, riskLevel, budget } = params;

    // Base calculations
    let recommendedPrice = basePrice;
    let winProbability = 0.5; // Base 50% probability
    let profitMargin = 0.15; // Base 15% profit margin
    let riskScore = 0.3; // Base risk score

    // Adjust for competitor count
    const competitorFactor = Math.max(0.1, 1 - (competitorCount * 0.1));
    recommendedPrice *= competitorFactor;
    winProbability *= competitorFactor;

    // Adjust for market conditions
    switch (marketConditions) {
      case 'stable':
        recommendedPrice *= 1.0;
        winProbability *= 1.1;
        riskScore *= 0.8;
        break;
      case 'competitive':
        recommendedPrice *= 0.9;
        winProbability *= 0.8;
        riskScore *= 1.2;
        break;
      case 'volatile':
        recommendedPrice *= 0.85;
        winProbability *= 0.7;
        riskScore *= 1.5;
        break;
    }

    // Adjust for risk level
    switch (riskLevel) {
      case 'low':
        recommendedPrice *= 1.05;
        profitMargin *= 1.2;
        riskScore *= 0.7;
        break;
      case 'medium':
        recommendedPrice *= 1.0;
        profitMargin *= 1.0;
        riskScore *= 1.0;
        break;
      case 'high':
        recommendedPrice *= 0.95;
        profitMargin *= 0.8;
        riskScore *= 1.4;
        break;
    }

    // Ensure price doesn't exceed budget
    if (recommendedPrice > budget * 0.9) {
      recommendedPrice = budget * 0.9;
      winProbability *= 0.9;
    }

    // Calculate final profit margin
    profitMargin = Math.max(0.05, (recommendedPrice - basePrice) / recommendedPrice);

    // Normalize values
    winProbability = Math.max(0.1, Math.min(0.95, winProbability));
    riskScore = Math.max(0.1, Math.min(1.0, riskScore));

    return {
      recommendedPrice: Math.round(recommendedPrice * 100) / 100,
      winProbability: Math.round(winProbability * 100) / 100,
      profitMargin: Math.round(profitMargin * 100) / 100,
      riskScore: Math.round(riskScore * 100) / 100,
      analysisData: {
        competitorFactor,
        marketConditions,
        riskLevel,
        basePrice,
        budget
      }
    };
  }
}

/**
 * Get all simulations for a project
 * GET /api/simulations/project/:projectId
 */
router.get('/project/:projectId', async (req: Request, res: Response): Promise<void> => {
  try {
    const { projectId } = req.params;
    const { page = 1, limit = 10 } = req.query;
    const offset = (Number(page) - 1) * Number(limit);

    // Verify project belongs to user
    const project = await mockDataStore.getProjectById(projectId);

    if (!project || project.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Project not found'
      });
      return;
    }

    // Get simulations with results
    const allSimulations = await mockDataStore.getSimulationsByProjectId(projectId);
    const total = allSimulations.length;
    const simulations = allSimulations.slice(offset, offset + Number(limit));

    // Add simulation results to each simulation
    const simulationsWithResults = await Promise.all(
      simulations.map(async (simulation) => {
        const result = await mockDataStore.getSimulationResult(simulation.id);
        return {
          ...simulation,
          simulation_results: result ? [result] : []
        };
      })
    );

    res.json({
      success: true,
      data: {
        simulations: simulationsWithResults,
        pagination: {
          page: Number(page),
          limit: Number(limit),
          total,
          totalPages: Math.ceil(total / Number(limit))
        }
      }
    });
  } catch (error) {
    console.error('Get simulations error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Get a specific simulation with results
 * GET /api/simulations/:id
 */
router.get('/:id', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;

    // Get simulation
    const simulation = await mockDataStore.getSimulationById(id);

    if (!simulation) {
      res.status(404).json({
        success: false,
        message: 'Simulation not found'
      });
      return;
    }

    // Get project info to verify ownership
    const project = await mockDataStore.getProjectById(simulation.project_id);

    if (!project || project.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Simulation not found'
      });
      return;
    }

    // Get simulation results
    const result = await mockDataStore.getSimulationResult(simulation.id);

    const simulationWithDetails = {
      ...simulation,
      projects: { id: project.id, user_id: project.user_id, name: project.name, budget: project.budget },
      simulation_results: result ? [result] : []
    };

    res.json({
      success: true,
      data: { simulation: simulationWithDetails }
    });
  } catch (error) {
    console.error('Get simulation error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Create and run a new simulation
 * POST /api/simulations
 */
router.post('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      projectId,
      name,
      basePrice,
      competitorCount,
      marketConditions,
      riskLevel
    } = req.body;

    // Validate input
    if (!projectId || !name || !basePrice || competitorCount === undefined) {
      res.status(400).json({
        success: false,
        message: 'Project ID, name, base price, and competitor count are required'
      });
      return;
    }

    // Validate numeric inputs
    if (typeof basePrice !== 'number' || basePrice <= 0) {
      res.status(400).json({
        success: false,
        message: 'Base price must be a positive number'
      });
      return;
    }

    if (typeof competitorCount !== 'number' || competitorCount < 0) {
      res.status(400).json({
        success: false,
        message: 'Competitor count must be a non-negative number'
      });
      return;
    }

    // Validate enum values
    const validMarketConditions = ['stable', 'competitive', 'volatile'];
    const validRiskLevels = ['low', 'medium', 'high'];

    if (!validMarketConditions.includes(marketConditions)) {
      res.status(400).json({
        success: false,
        message: 'Invalid market conditions. Must be: stable, competitive, or volatile'
      });
      return;
    }

    if (!validRiskLevels.includes(riskLevel)) {
      res.status(400).json({
        success: false,
        message: 'Invalid risk level. Must be: low, medium, or high'
      });
      return;
    }

    // Verify project belongs to user and get budget
    const project = await mockDataStore.getProjectById(projectId);

    if (!project || project.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Project not found'
      });
      return;
    }

    // Create simulation record
    const simulation = await mockDataStore.createSimulation({
      project_id: projectId,
      name,
      base_price: basePrice,
      competitor_count: competitorCount,
      market_conditions: marketConditions,
      risk_level: riskLevel
    });

    // Run price simulation algorithm
    const simulationResult = PriceSimulator.calculateRecommendedPrice({
      basePrice,
      competitorCount,
      marketConditions,
      riskLevel,
      budget: project.budget
    });

    // Save simulation results
    const result = await mockDataStore.createSimulationResult({
      simulation_id: simulation.id,
      recommended_price: simulationResult.recommendedPrice,
      win_probability: simulationResult.winProbability,
      profit_margin: simulationResult.profitMargin,
      risk_score: simulationResult.riskScore,
      analysis_data: simulationResult.analysisData
    });

    res.status(201).json({
      success: true,
      message: 'Simulation completed successfully',
      data: {
        simulation: {
          ...simulation,
          simulation_results: [result]
        }
      }
    });
  } catch (error) {
    console.error('Create simulation error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

/**
 * Delete a simulation
 * DELETE /api/simulations/:id
 */
router.delete('/:id', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;

    // Verify simulation belongs to user
    const simulation = await mockDataStore.getSimulationById(id);

    if (!simulation) {
      res.status(404).json({
        success: false,
        message: 'Simulation not found'
      });
      return;
    }

    const project = await mockDataStore.getProjectById(simulation.project_id);

    if (!project || project.user_id !== req.user!.userId) {
      res.status(404).json({
        success: false,
        message: 'Simulation not found'
      });
      return;
    }

    // Delete simulation and its results
    await mockDataStore.deleteSimulation(id);

    res.json({
      success: true,
      message: 'Simulation deleted successfully'
    });
  } catch (error) {
    console.error('Delete simulation error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

export default router;
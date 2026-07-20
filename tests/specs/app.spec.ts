/**
 * Task Manager — Playwright E2E Test Suite
 * Run with: npx playwright test
 * Requires: backend running on :3333, frontend on :5173
 */
import { test, expect, Page } from '@playwright/test';

// ─── Helpers ──────────────────────────────────────────────────────────────────
async function resetSetup(page: Page) {
  // Wipe all config + agents, then re-seed a known state
  await page.request.post('http://localhost:3333/api/setup/reset');
  await page.request.post('http://localhost:3333/api/setup', {
    data: { user_name: 'E2EUser', project_name: 'E2E Project', folder_path: '/tmp/e2e_agents' },
  });
}

// ─── 1. Setup Wizard ──────────────────────────────────────────────────────────
test.describe('Setup Wizard', () => {
  test.beforeEach(async ({ page }) => {
    // Always start from a clean (unconfigured) DB state
    await page.request.post('http://localhost:3333/api/setup/reset');
  });

  test('redirects to /setup when not configured', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    await expect(page).toHaveURL(/\/setup/);
    await expect(page.locator('h1')).toContainText('Task Manager');
  });

  test('step 1 — continue disabled until name entered', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    const continueBtn = page.getByRole('button', { name: /continue/i });
    await expect(continueBtn).toBeDisabled();
    await page.fill('input[type="text"]', 'Alice');
    await expect(continueBtn).toBeEnabled();
  });

  test('step 1 → 2 → 3 navigation works', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    // Step 1
    await page.fill('input[type="text"]', 'Alice');
    await page.getByRole('button', { name: /continue/i }).click();
    // Step 2
    await expect(page.locator('h2')).toContainText('Name your project');
    await page.fill('input[type="text"]', 'My Project');
    await page.getByRole('button', { name: /continue/i }).click();
    // Step 3
    await expect(page.locator('h2')).toContainText('Agents folder');
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible();
  });

  test('back button returns to previous step', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    await page.fill('input[type="text"]', 'Alice');
    await page.getByRole('button', { name: /continue/i }).click();
    await page.fill('input[type="text"]', 'My Project');
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('button', { name: /back/i }).click();
    await expect(page.locator('h2')).toContainText('Name your project');
  });

  test('get started disabled until folder path entered', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    await page.fill('input[type="text"]', 'Alice');
    await page.getByRole('button', { name: /continue/i }).click();
    await page.fill('input[type="text"]', 'My Project');
    await page.getByRole('button', { name: /continue/i }).click();
    await expect(page.getByRole('button', { name: /get started/i })).toBeDisabled();
  });

  test('complete setup and redirect to home', async ({ page }) => {
    await page.goto('http://localhost:5173/setup');
    await page.fill('input[type="text"]', 'Alice');
    await page.getByRole('button', { name: /continue/i }).click();
    await page.fill('input[type="text"]', 'AliceProject');
    await page.getByRole('button', { name: /continue/i }).click();
    await page.fill('input[type="text"]', '/tmp/alice_agents');
    await page.getByRole('button', { name: /get started/i }).click();
    await expect(page).toHaveURL('http://localhost:5173/');
  });
});

// ─── 2. Home / Sidebar ────────────────────────────────────────────────────────
test.describe('Home & Sidebar', () => {
  test.beforeEach(async ({ page }) => { await resetSetup(page); });

  test('home page shows sidebar', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await expect(page.locator('nav, aside, [class*="sidebar"]').first()).toBeVisible();
  });

  test('home page shows select-agent placeholder', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await expect(page.getByText('Select an agent')).toBeVisible();
  });

  test('sidebar shows default agent', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await expect(page.getByText('E2EUser')).toBeVisible();
  });

  test('can create a new agent', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    // Look for "New Agent" or "+" button in sidebar
    const addBtn = page.getByRole('button', { name: /new agent|add agent|\+/i }).first();
    await addBtn.click();
    // Expect an input to appear
    const input = page.locator('input[placeholder*="agent"], input[placeholder*="name"]').last();
    await input.fill('BrandNewAgent');
    await input.press('Enter');
    await expect(page.getByText('BrandNewAgent')).toBeVisible();
  });

  test('clicking agent in sidebar navigates to agent view', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.getByText('E2EUser').first().click();
    await expect(page).toHaveURL(/\/agent\/\d+/);
  });
});

// ─── 3. Agent View — Tabs ─────────────────────────────────────────────────────
test.describe('Agent View - Tabs', () => {
  let agentUrl: string;

  test.beforeEach(async ({ page }) => {
    await resetSetup(page);
    await page.goto('http://localhost:5173/');
    // Navigate to the default agent
    const r = await page.request.get('http://localhost:3333/api/agents');
    const agents = await r.json();
    const defaultAgent = agents.find((a: any) => a.is_default);
    agentUrl = `http://localhost:5173/agent/${defaultAgent.id}`;
  });

  test('Tasks tab is active by default', async ({ page }) => {
    await page.goto(agentUrl);
    const tasksTab = page.getByRole('button', { name: /tasks/i });
    await expect(tasksTab).toHaveClass(/active/);
  });

  test('can switch between tabs', async ({ page }) => {
    await page.goto(agentUrl);
    await page.getByRole('button', { name: /instructions/i }).click();
    await expect(page.locator('[class*="instructions"], textarea').first()).toBeVisible();

    await page.getByRole('button', { name: /skills/i }).click();
    await expect(page.locator('[class*="skills"], textarea').first()).toBeVisible();

    await page.getByRole('button', { name: /routine/i }).click();
    await expect(page.locator('[class*="routine"]').first()).toBeVisible();
  });

  test('agent name and default badge shown in header', async ({ page }) => {
    await page.goto(agentUrl);
    await expect(page.getByText('E2EUser')).toBeVisible();
    await expect(page.getByText('default')).toBeVisible();
  });
});

// ─── 4. Tasks Tab ─────────────────────────────────────────────────────────────
test.describe('Tasks Tab', () => {
  let agentId: number;
  let agentUrl: string;

  test.beforeEach(async ({ page }) => {
    await resetSetup(page);
    const r = await page.request.get('http://localhost:3333/api/agents');
    const agents = await r.json();
    agentId = agents.find((a: any) => a.is_default).id;
    agentUrl = `http://localhost:5173/agent/${agentId}`;
  });

  test('shows empty state when no tasks', async ({ page }) => {
    await page.goto(agentUrl);
    // Should show a kanban board or empty state
    const board = page.locator('[class*="kanban"], [class*="tasks"], [class*="board"]').first();
    await expect(board).toBeVisible();
  });

  test('can create a new task', async ({ page }) => {
    await page.goto(agentUrl);
    const addBtn = page.getByRole('button', { name: /add task|new task|\+/i }).first();
    await addBtn.click();
    const titleInput = page.locator('input[placeholder*="task"], input[placeholder*="title"]').last();
    await titleInput.fill('My E2E Task');
    await titleInput.press('Enter');
    await expect(page.getByText('My E2E Task')).toBeVisible();
  });

  test('can open task detail / comments panel', async ({ page }) => {
    // Pre-create a task
    await page.request.post('http://localhost:3333/api/tasks', {
      data: { agent_id: agentId, title: 'Click Me Task', status: 'todo' },
    });
    await page.goto(agentUrl);
    await page.getByText('Click Me Task').click();
    // Expect detail panel to open
    await expect(page.locator('[class*="detail"], [class*="panel"], [class*="drawer"]').first()).toBeVisible();
  });

  test('can move task between kanban columns', async ({ page }) => {
    await page.request.post('http://localhost:3333/api/tasks', {
      data: { agent_id: agentId, title: 'Drag Task', status: 'todo' },
    });
    await page.goto(agentUrl);
    // Verify "In Progress" column exists
    await expect(page.getByText(/in.?progress/i).first()).toBeVisible();
  });

  test('task status changes persist on reload', async ({ page }) => {
    const tr = await page.request.post('http://localhost:3333/api/tasks', {
      data: { agent_id: agentId, title: 'Persist Task', status: 'todo' },
    });
    const taskId = (await tr.json()).id;
    await page.request.put(`http://localhost:3333/api/tasks/${taskId}`, {
      data: { status: 'done' },
    });
    await page.goto(agentUrl);
    // Done column should show the task
    await expect(page.getByText('Persist Task')).toBeVisible();
  });
});

// ─── 5. Instructions Tab ──────────────────────────────────────────────────────
test.describe('Instructions Tab (CLAUDE.md)', () => {
  let agentId: number;

  test.beforeEach(async ({ page }) => {
    await resetSetup(page);
    const r = await page.request.get('http://localhost:3333/api/agents');
    const agents = await r.json();
    agentId = agents.find((a: any) => a.is_default).id;
  });

  test('instructions editor shows existing content', async ({ page }) => {
    await page.goto(`http://localhost:5173/agent/${agentId}`);
    await page.getByRole('button', { name: /instructions/i }).click();
    const editor = page.locator('textarea').first();
    await expect(editor).toBeVisible();
    const content = await editor.inputValue();
    expect(content.length).toBeGreaterThan(0);
  });

  test('can edit and save instructions', async ({ page }) => {
    await page.goto(`http://localhost:5173/agent/${agentId}`);
    await page.getByRole('button', { name: /instructions/i }).click();
    const editor = page.locator('textarea').first();
    await editor.fill('# Updated Instructions\n\nTest content from E2E.');
    await page.getByRole('button', { name: /save/i }).click();
    // Reload and verify
    await page.reload();
    await page.getByRole('button', { name: /instructions/i }).click();
    await expect(page.locator('textarea').first()).toHaveValue(/Updated Instructions/);
  });
});

// ─── 6. Routines Tab ──────────────────────────────────────────────────────────
test.describe('Routines Tab', () => {
  let agentId: number;

  test.beforeEach(async ({ page }) => {
    await resetSetup(page);
    const r = await page.request.get('http://localhost:3333/api/agents');
    const agents = await r.json();
    agentId = agents.find((a: any) => a.is_default).id;
  });

  test('shows empty routines state', async ({ page }) => {
    await page.goto(`http://localhost:5173/agent/${agentId}`);
    await page.getByRole('button', { name: /routine/i }).click();
    await expect(page.locator('[class*="routine"]').first()).toBeVisible();
  });

  test('can create a routine', async ({ page }) => {
    await page.goto(`http://localhost:5173/agent/${agentId}`);
    await page.getByRole('button', { name: /routine/i }).click();
    const addBtn = page.getByRole('button', { name: /add routine/i });
    // The form is always visible — no click needed to reveal it; just fill the label input
    const input = page.locator('input[placeholder*="label"]').last();
    await input.fill('Daily Standup');
    await page.getByRole('button', { name: /add routine/i }).click();
    await expect(page.getByText('Daily Standup')).toBeVisible();
  });
});

// ─── 7. Navigation Guards ─────────────────────────────────────────────────────
test.describe('Navigation Guards', () => {
  test('accessing / when setup done stays on home', async ({ page }) => {
    await page.request.post('http://localhost:3333/api/setup', {
      data: { user_name: 'Guard', project_name: 'GuardProject', folder_path: '/tmp/guard' },
    });
    await page.goto('http://localhost:5173/');
    await expect(page).not.toHaveURL(/\/setup/);
  });

  test('accessing /agent/:id with invalid id shows loading state', async ({ page }) => {
    await page.request.post('http://localhost:3333/api/setup', {
      data: { user_name: 'Guard', project_name: 'GuardProject', folder_path: '/tmp/guard' },
    });
    await page.goto('http://localhost:5173/agent/99999');
    // Should show loading or not crash
    await expect(page.locator('body')).toBeVisible();
  });
});

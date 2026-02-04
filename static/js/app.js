// App State
const state = {
    currentUser: null,
    currentView: 'dashboard',
    token: localStorage.getItem('erp_token')
};

// DOM Elements
const contentArea = document.getElementById('content-area');
const pageTitle = document.getElementById('page-title');
const navLinks = document.querySelectorAll('.nav-item');

// API Configuration
const API_BASE = '/api';

// Router
function navigateTo(view) {
    state.currentView = view;
    
    // Update Sidebar
    navLinks.forEach(link => {
        if(link.dataset.view === view) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Render View
    switch(view) {
        case 'dashboard':
            renderDashboard();
            break;
        case 'projects':
            renderProjects();
            break;
        case 'tasks':
            renderTasks();
            break;
        case 'users':
            renderUsers();
            break;
        case 'settings':
            renderSettings();
            break;
        default:
            renderDashboard();
    }
}

// Render Functions
function renderDashboard() {
    pageTitle.textContent = 'Dashboard';
    contentArea.innerHTML = `
        <div class="grid-container">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Total Projects</h3>
                    <i class="fas fa-project-diagram" style="color: var(--primary-color)"></i>
                </div>
                <div class="stat-value">12</div>
                <div class="stat-label">4 Active, 8 Completed</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Pending Tasks</h3>
                    <i class="fas fa-tasks" style="color: var(--warning-color)"></i>
                </div>
                <div class="stat-value">24</div>
                <div class="stat-label">3 High Priority</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Team Members</h3>
                    <i class="fas fa-users" style="color: var(--success-color)"></i>
                </div>
                <div class="stat-value">8</div>
                <div class="stat-label">Active now</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Revenue (YTD)</h3>
                    <i class="fas fa-chart-line" style="color: var(--secondary-color)"></i>
                </div>
                <div class="stat-value">$142k</div>
                <div class="stat-label">+12% from last month</div>
            </div>
        </div>

        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">Recent Activity</h3>
            </div>
            <p>System operational. API version 1.0.0 running.</p>
        </div>
    `;
}

function renderProjects() {
    pageTitle.textContent = 'Projects';
    contentArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Active Projects</h3>
                <button class="btn btn-primary">New Project</button>
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="text-align: left; border-bottom: 2px solid var(--border-color);">
                        <th style="padding: 1rem 0;">Project Name</th>
                        <th>Status</th>
                        <th>Due Date</th>
                        <th>Team</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 1rem 0;">ERP Implementation</td>
                        <td><span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 999px; font-size: 0.75rem;">In Progress</span></td>
                        <td>Mar 15, 2026</td>
                        <td>Dev Team A</td>
                    </tr>
                    <tr>
                        <td style="padding: 1rem 0;">Marketing Website</td>
                        <td><span style="background: #dcfce7; color: #166534; padding: 0.25rem 0.5rem; border-radius: 999px; font-size: 0.75rem;">Completed</span></td>
                        <td>Jan 20, 2026</td>
                        <td>Marketing</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// Placeholder renders for other views
function renderTasks() {
    pageTitle.textContent = 'Tasks';
    contentArea.innerHTML = '<div class="card"><p>Task management module loading...</p></div>';
}

function renderUsers() {
    pageTitle.textContent = 'User Management';
    contentArea.innerHTML = '<div class="card"><p>User list fetching from /api/users...</p></div>';
}

function renderSettings() {
    pageTitle.textContent = 'System Settings';
    contentArea.innerHTML = `
        <div class="card">
            <h3 class="card-title" style="margin-bottom: 1rem;">General Settings</h3>
            <div class="form-group">
                <label class="form-label">System Name</label>
                <input type="text" class="form-input" value="ERP System v1">
            </div>
            <div class="form-group">
                <label class="form-label">Admin Email</label>
                <input type="email" class="form-input" value="admin@example.com">
            </div>
            <button class="btn btn-primary">Save Changes</button>
        </div>
    `;
}

// specific logic for check auth will go here
// For now, init app
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            navigateTo(view);
        });
    });

    // Initial Load
    navigateTo('dashboard');
});

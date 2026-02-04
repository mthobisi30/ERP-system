// App State
const state = {
    token: localStorage.getItem('erp_token')
};

// API Base
const API_BASE = '/api';

// DOM Elements
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');

// Auth Headers
function getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
    return headers;
}

// Login Handler
async function handleLogin(e) {
    if(e) e.preventDefault();
    if(loginError) loginError.style.display = 'none';
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Login failed');
        
        localStorage.setItem('erp_token', data.access_token);
        window.location.href = '/dashboard';
    } catch (err) {
        if(loginError) {
            loginError.textContent = err.message;
            loginError.style.display = 'block';
            loginError.classList.remove('hidden');
        }
    }
}

// Logout Handler
function handleLogout(e) {
    if(e) e.preventDefault();
    localStorage.removeItem('erp_token');
    window.location.href = '/login';
}

// Data Fetching
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, { headers: getHeaders() });
        if (response.status === 401) {
            localStorage.removeItem('erp_token');
            window.location.href = '/login';
            return null;
        }
        return await response.json();
    } catch (err) {
        console.error('Fetch error:', err);
        return null;
    }
}

// Tailwind Table Render
function renderTable(containerId, list, title) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!list || list.length === 0) {
        container.innerHTML = `
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
                <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
                    <i class="fas fa-folder-open text-2xl"></i>
                </div>
                <h3 class="text-lg font-medium text-gray-900">No records found</h3>
                <p class="text-gray-500 mt-1">There are no items to display in this view yet.</p>
                <button class="mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm" onclick="window.openCreateModal('${VIEW_KEY}')">
                    <i class="fas fa-plus mr-2"></i> Create New
                </button>
            </div>`;
        return;
    }

    const firstItem = list[0];
    const columns = Object.keys(firstItem).slice(0, 5);
    
    // Header Generation
    let headers = columns.map(c => 
        `<th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">${c.replace(/_/g, ' ')}</th>`
    ).join('');
    headers += `<th scope="col" class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>`;
    
    // Row Generation
    const rows = list.map(item => {
        const cells = columns.map(col => {
            let val = item[col];
            if (val === null || val === undefined) val = '-';
            if (typeof val === 'object') val = JSON.stringify(val).substring(0, 20) + '...';
            
            if (col.includes('status')) {
                const colors = {
                    'active': 'green', 'completed': 'green', 'paid': 'green',
                    'pending': 'yellow', 'draft': 'yellow', 'todo': 'yellow',
                    'lost': 'red', 'closed_lost': 'red', 'cancelled': 'red'
                };
                const color = colors[val.toLowerCase()] || 'gray';
                val = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800 capitalize">${val}</span>`;
            }
            
            return `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${val}</td>`;
        }).join('');

        const actions = `
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="window.openEditModal('${VIEW_KEY}', '${item.id}')" class="text-primary-600 hover:text-primary-900 mr-3 transition-colors">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="window.deleteRecord('${VIEW_KEY}', '${item.id}')" class="text-red-400 hover:text-red-600 transition-colors">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;

        return `<tr class="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0">${cells}${actions}</tr>`;
    }).join('');

    container.innerHTML = `
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
             <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                    <p class="text-sm text-gray-500">Managing ${list.length} records</p>
                </div>
                <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm text-sm font-medium" onclick="window.openCreateModal('${VIEW_KEY}')">
                    <i class="fas fa-plus mr-2"></i> Add New
                </button>
            </div>
            <div id="create-modal" class="fixed inset-0 bg-gray-900/50 hidden items-center justify-center p-4 z-50">
                <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
                    <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-2xl">
                        <h3 class="text-lg font-bold text-gray-900" id="modal-title">Create New</h3>
                        <button onclick="document.getElementById('create-modal').classList.add('hidden'); document.getElementById('create-modal').classList.remove('flex');" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
                    </div>
                    <form id="dynamic-create-form" class="p-6 space-y-4">
                        <div id="modal-fields" class="space-y-4"></div>
                        <div class="flex justify-end gap-3 mt-6">
                            <button type="button" onclick="document.getElementById('create-modal').classList.add('hidden'); document.getElementById('create-modal').classList.remove('flex');" class="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">Cancel</button>
                            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">Save Record</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>${headers}</tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${rows}
                    </tbody>
                </table>
            </div>
            <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between">
                <span class="text-xs text-gray-500">Showing 1 to ${Math.min(20, list.length)} of ${list.length} results</span>
                <div class="flex gap-2">
                    <button class="px-3 py-1 border border-gray-300 rounded text-xs text-gray-600 hover:bg-white disabled:opacity-50" disabled>Previous</button>
                    <button class="px-3 py-1 border border-gray-300 rounded text-xs text-gray-600 hover:bg-white disabled:opacity-50" disabled>Next</button>
                </div>
            </div>
        </div>
    `;
}

// Minimal Dashboard Render (NO STATS CARDS but dynamically populated)
function renderDashboard(data) {
    const container = document.getElementById('dashboard-container');
    if (!container) return;
    
    // Check if we have the stats data (the initial load)
    const stats = data.stats || data; // Handle both direct and nested data
    
    container.innerHTML = `
        <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">Welcome back, Admin! 👋</h2>
            <p class="text-gray-500">Here is what's happening with your business today.</p>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                <a href="/projects" class="p-4 bg-orange-50 rounded-xl border border-orange-100 hover:shadow-md transition-all group">
                    <p class="text-xs font-bold text-orange-600 uppercase group-hover:text-primary-600">Active Projects</p>
                    <p class="text-2xl font-bold text-slate-800">${stats.projects?.active || 0}</p>
                </a>
                <a href="/tasks" class="p-4 bg-blue-50 rounded-xl border border-blue-100 hover:shadow-md transition-all group">
                    <p class="text-xs font-bold text-blue-600 uppercase group-hover:text-blue-700">Pending Tasks</p>
                    <p class="text-2xl font-bold text-slate-800">${stats.tasks?.pending || 0}</p>
                </a>
                <a href="/customers" class="p-4 bg-green-50 rounded-xl border border-green-100 hover:shadow-md transition-all group">
                    <p class="text-xs font-bold text-green-600 uppercase group-hover:text-green-700">Total Customers</p>
                    <p class="text-2xl font-bold text-slate-800">${stats.customers || 0}</p>
                </a>
                <a href="/sales" class="p-4 bg-purple-50 rounded-xl border border-purple-100 hover:shadow-md transition-all group">
                    <p class="text-xs font-bold text-purple-600 uppercase group-hover:text-purple-700">Total Sales</p>
                    <p class="text-2xl font-bold text-slate-800">$${(stats.sales || 0).toLocaleString()}</p>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8" id="activity-grid">
            <!-- Content will be injected by loadRecentActivity -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-pulse">
                <div class="h-64 bg-gray-50"></div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-pulse">
                <div class="h-64 bg-gray-50"></div>
            </div>
        </div>
    `;

    // Fetch and render recent activity
    loadRecentActivity();
}

async function loadRecentActivity() {
    const grid = document.getElementById('activity-grid');
    if (!grid) return;

    const data = await fetchData('/dashboard/recent-activity');
    if (!data) return;

    grid.innerHTML = `
        <!-- Recent Projects Preview -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 font-semibold text-gray-700 flex justify-between items-center">
                <span>Recent Projects</span>
                <a href="/projects" class="text-primary-600 text-sm hover:underline">View All</a>
            </div>
            <div class="p-0">
                ${data.projects?.length > 0 ? `
                    <ul class="divide-y divide-gray-100">
                        ${data.projects.map(p => `
                            <li class="px-6 py-4 flex justify-between items-center hover:bg-gray-50 transition-colors">
                                <div>
                                    <p class="text-sm font-medium text-gray-900">${p.name}</p>
                                    <p class="text-xs text-gray-500">${p.status || 'Active'}</p>
                                </div>
                                <span class="text-xs text-gray-400">${new Date(p.created_at).toLocaleDateString()}</span>
                            </li>
                        `).join('')}
                    </ul>
                ` : '<div class="p-8 text-center text-gray-400 text-sm">No recent projects.</div>'}
            </div>
        </div>

        <!-- Recent Tasks Preview -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 font-semibold text-gray-700 flex justify-between items-center">
                <span>Recent Tasks</span>
                 <a href="/tasks" class="text-primary-600 text-sm hover:underline">View All</a>
            </div>
            <div class="p-0">
                ${data.tasks?.length > 0 ? `
                    <ul class="divide-y divide-gray-100">
                        ${data.tasks.map(t => `
                            <li class="px-6 py-4 flex justify-between items-center hover:bg-gray-50 transition-colors">
                                <div>
                                    <p class="text-sm font-medium text-gray-900">${t.title}</p>
                                    <p class="text-xs text-gray-500">${t.status || 'Pending'}</p>
                                </div>
                                <span class="text-xs text-gray-400">${new Date(t.created_at).toLocaleDateString()}</span>
                            </li>
                        `).join('')}
                    </ul>
                ` : '<div class="p-8 text-center text-gray-400 text-sm">No recent tasks.</div>'}
            </div>
        </div>
    `;
}

// Init
document.addEventListener('DOMContentLoaded', async () => {
    // Login Page Handler
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        return;
    }
    
    // Register Page Handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        return;
    }

    // Auth Check
    if (!state.token) {
        window.location.href = '/login';
        return;
    }

    // Logout Button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

    // Tools Page Handlers
    const invoiceForm = document.getElementById('invoice-form');
    if (invoiceForm) {
        invoiceForm.addEventListener('submit', handleCreateInvoice);
    }
    const quoteForm = document.getElementById('quote-form');
    if (quoteForm) {
        quoteForm.addEventListener('submit', handleCreateQuote);
    }

    // Page Specific Loading
    if (typeof API_ENDPOINT !== 'undefined' && API_ENDPOINT) {
        const dashboardContainer = document.getElementById('dashboard-container');
        const listContainer = document.getElementById('list-container');
        const target = dashboardContainer || listContainer || document.getElementById('content-area');
        
        if(target) target.innerHTML = '<div class="flex justify-center items-center h-64"><i class="fas fa-circle-notch fa-spin text-primary-500 text-3xl"></i></div>';

        const data = await fetchData(API_ENDPOINT);
        if (data) {
            // Check context
            if (window.location.pathname.includes('/dashboard')) {
                renderDashboard(data);
            } else if (window.location.pathname.includes('/profile')) {
                renderProfile(data);
            } else if (typeof VIEW_KEY !== 'undefined') {
                 // Handle list extraction
                let list = [];
                 if (Array.isArray(data)) {
                    list = data;
                } else if (data[VIEW_KEY]) {
                    list = data[VIEW_KEY];
                } else {
                    const firstArrayKey = Object.keys(data).find(k => Array.isArray(data[k]));
                    if (firstArrayKey) list = data[firstArrayKey];
                }
                renderTable('list-container', list, document.title.split('|')[1].trim());
            }
        }
    }

    // Always fetch user info for sidebar
    const user = await fetchData('/auth/me');
    if (user) {
        document.getElementById('nav-user-name').textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
        document.getElementById('nav-user-email').textContent = user.email;
        document.getElementById('nav-user-avatar').textContent = (user.first_name?.[0] || user.username?.[0] || '?').toUpperCase();
    }
});

function renderProfile(user) {
    const container = document.getElementById('profile-container');
    if (!container) return;

    // Populate fields
    document.getElementById('profile-name-header').textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
    document.getElementById('profile-role-header').textContent = user.role || 'User';
    document.getElementById('profile-username').textContent = user.username;
    document.getElementById('profile-email').textContent = user.email;
    document.getElementById('profile-avatar-large').textContent = (user.first_name?.[0] || user.username?.[0] || '?').toUpperCase();

    // Fill form
    document.getElementById('edit-first-name').value = user.first_name || '';
    document.getElementById('edit-last-name').value = user.last_name || '';
    document.getElementById('edit-username').value = user.username || '';
    document.getElementById('edit-email').value = user.email || '';

    // Handle form submit
    const form = document.getElementById('edit-profile-form');
    form.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const body = Object.fromEntries(formData.entries());
        try {
            const res = await fetch(`${API_BASE}/users/${user.id}`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify(body)
            });
            if (res.ok) {
                alert('Profile updated!');
                window.location.reload();
            } else {
                alert('Update failed');
            }
        } catch (e) { alert('Error'); }
    };
}

// Register Handler
async function handleRegister(e) {
    if(e) e.preventDefault();
    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    if(errorDiv) errorDiv.classList.add('hidden');
    if(successDiv) successDiv.classList.add('hidden');

    const fullName = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        if(errorDiv) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.classList.remove('hidden');
        }
        return;
    }

    const [firstName, ...lastNameParts] = fullName.split(' ');
    const lastName = lastNameParts.join(' ') || '';
    const username = email.split('@')[0];

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email, 
                password,
                username,
                first_name: firstName,
                last_name: lastName
            })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Registration failed');
        
        if(successDiv) {
            successDiv.textContent = 'Account created successfully! Redirecting...';
            successDiv.classList.remove('hidden');
        }
        
        setTimeout(() => window.location.href = '/login', 2000);
    } catch (err) {
        if(errorDiv) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    }
}

// Create Invoice Handler
// Create Invoice Handler
async function handleCreateInvoice(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const itemRows = document.querySelectorAll('#invoice-items > div');
    const items = Array.from(itemRows).map(row => ({
        description: row.querySelector('input[placeholder="Description"]')?.value || row.querySelector('[name="item_description"]')?.value,
        quantity: parseFloat(row.querySelector('input[placeholder="Qty"]')?.value || row.querySelector('[name="item_qty"]')?.value || 0),
        unit_price: parseFloat(row.querySelector('input[placeholder="Price"]')?.value || row.querySelector('[name="item_price"]')?.value || 0)
    }));

    const data = {
        invoice_number: 'INV-' + Date.now().toString().slice(-6),
        customer_id: formData.get('client_name'),
        due_date: formData.get('due_date'),
        status: 'draft',
        total_amount: items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0),
        items: items
    };

    try {
        const response = await fetch(`${API_BASE}/invoices`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if(response.ok) {
            alert('Invoice created successfully!');
            window.location.href = '/invoices';
        } else {
            alert('Failed to create invoice');
        }
    } catch(err) {
        console.error(err);
        alert('Error creating invoice');
    }
}

// Create Quote Handler
async function handleCreateQuote(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const itemRows = document.querySelectorAll('#quote-items > div');
    const items = Array.from(itemRows).map(row => ({
        description: row.querySelector('input[placeholder*="Product"]')?.value || row.querySelector('[name="item_description"]')?.value,
        quantity: parseFloat(row.querySelector('input[placeholder="Qty"]')?.value || row.querySelector('[name="item_qty"]')?.value || 0),
        unit_price: parseFloat(row.querySelector('input[placeholder*="Price"]')?.value || row.querySelector('[name="item_price"]')?.value || 0)
    }));

    const data = {
        quotation_number: 'Q-' + Date.now().toString().slice(-6),
        customer_id: formData.get('client_name'),
        valid_until: formData.get('valid_until'),
        status: 'draft',
        total_amount: items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0),
        items: items
    };

    try {
        const response = await fetch(`${API_BASE}/sales/quotations`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if(response.ok) {
            alert('Quote generated successfully!');
            window.location.href = '/quotations';
        } else {
            alert('Failed to create quote');
        }
    } catch(err) {
        console.error(err);
        alert('Error creating quotation');
    }
}

// View Schema Mapping for Dynamic Creation
const VIEW_SCHEMAS = {
    'projects': { title: 'Project', fields: [ {id: 'name', label: 'Name'}, {id: 'customer_id', label: 'Customer ID (UUID)'}, {id: 'status', label: 'Status', type: 'select', options: ['active', 'paused', 'completed']} ] },
    'tasks': { title: 'Task', fields: [ {id: 'title', label: 'Title'}, {id: 'project_id', label: 'Project ID (UUID)'}, {id: 'status', label: 'Status', type: 'select', options: ['todo', 'in_progress', 'done']}, {id: 'due_date', label: 'Due Date', type: 'date'} ] },
    'users': { title: 'User', fields: [ {id: 'username', label: 'Username'}, {id: 'email', label: 'Email', type: 'email'}, {id: 'role', label: 'Role', type: 'select', options: ['admin', 'manager', 'employee']} ] },
    'inventory': { title: 'Inventory Item', fields: [ {id: 'product_id', label: 'Product ID (UUID)'}, {id: 'warehouse_id', label: 'Warehouse ID (UUID)'}, {id: 'quantity_on_hand', label: 'Quantity', type: 'number'} ] },
    'products': { title: 'Product', fields: [ {id: 'name', label: 'Product Name'}, {id: 'sku', label: 'SKU'}, {id: 'unit_price', label: 'Price', type: 'number'} ] },
    'customers': { title: 'Customer', fields: [ {id: 'name', label: 'Company Name'}, {id: 'email', label: 'Email'}, {id: 'phone', label: 'Phone'} ] },
    'hr': { title: 'Employee', fields: [ {id: 'first_name', label: 'First Name'}, {id: 'last_name', label: 'Last Name'}, {id: 'position', label: 'Position'} ] },
    'leads': { title: 'Lead', fields: [ {id: 'name', label: 'Lead Name'}, {id: 'email', label: 'Email'}, {id: 'status', label: 'Status', type: 'select', options: ['new', 'contacted', 'qualified', 'lost']} ] },
    'opportunities': { title: 'Opportunity', fields: [ {id: 'name', label: 'Opportunity Name'}, {id: 'amount', label: 'Estimated Value', type: 'number'}, {id: 'stage', label: 'Stage', type: 'select', options: ['discovery', 'proposal', 'negotiation', 'closed_won', 'closed_lost']} ] },
    'suppliers': { title: 'Supplier', fields: [ {id: 'name', label: 'Supplier Name'}, {id: 'contact_person', label: 'Contact Person'}, {id: 'email', label: 'Email'} ] },
    'warehouses': { title: 'Warehouse', fields: [ {id: 'name', label: 'Warehouse Name'}, {id: 'code', label: 'Code'} ] },
    'tickets': { title: 'Support Ticket', fields: [ {id: 'subject', label: 'Subject'}, {id: 'priority', label: 'Priority', type: 'select', options: ['low', 'medium', 'high', 'urgent']} ] },
    'procurement': { title: 'Purchase Order', fields: [ {id: 'supplier_id', label: 'Supplier ID'}, {id: 'total_amount', label: 'Amount', type: 'number'}, {id: 'status', label: 'Status', type: 'select', options: ['draft', 'ordered', 'received', 'cancelled']} ] },
    'accounting': { title: 'Account', fields: [{id: 'name', label: 'Account Name'}, {id: 'code', label: 'Account Code'}, {id: 'type', label: 'Type', type: 'select', options: ['asset', 'liability', 'equity', 'revenue', 'expense']}] },
    'journal_entries': { title: 'Journal Entry', fields: [{id: 'ref_number', label: 'Reference'}, {id: 'description', label: 'Description'}, {id: 'date', label: 'Date', type: 'date'}] },
    'attendance': { title: 'Attendance Record', fields: [{id: 'employee_id', label: 'Employee ID'}, {id: 'check_in', label: 'Check In', type: 'datetime-local'}, {id: 'status', label: 'Status', type: 'select', options: ['present', 'late', 'absent']}] },
    'leaves': { title: 'Leave Request', fields: [{id: 'employee_id', label: 'Employee ID'}, {id: 'start_date', label: 'Start Date', type: 'date'}, {id: 'end_date', label: 'End Date', type: 'date'}, {id: 'status', label: 'Status', type: 'select', options: ['pending', 'approved', 'rejected']}] },
    'invoices': { title: 'Invoice', fields: [{id: 'invoice_number', label: 'Invoice #'}, {id: 'customer_id', label: 'Customer ID'}, {id: 'total_amount', label: 'Amount', type: 'number'}] },
    'expenses': { title: 'Expense', fields: [{id: 'category', label: 'Category'}, {id: 'amount', label: 'Amount', type: 'number'}, {id: 'date', label: 'Date', type: 'date'}] },
    'schedule': { title: 'Event', fields: [{id: 'title', label: 'Title'}, {id: 'start_time', label: 'Start', type: 'datetime-local'}, {id: 'end_time', label: 'End', type: 'datetime-local'}] },
    'documents': { title: 'Document', fields: [{id: 'name', label: 'Document Name'}, {id: 'type', label: 'Type'}] },
    'quotations': { title: 'Quotation', fields: [{id: 'quotation_number', label: 'Quotation #'}, {id: 'customer_id', label: 'Customer ID'}, {id: 'total_amount', label: 'Amount', type: 'number'}] },
    'sales': { title: 'Sales Order', fields: [{id: 'order_number', label: 'Order #'}, {id: 'customer_id', label: 'Customer ID'}] },
    'performance': { title: 'Performance Review', fields: [{id: 'employee_id', label: 'Employee ID'}, {id: 'rating', label: 'Rating (1-5)', type: 'number'}] },
    'time-tracking': { title: 'Time Entry', fields: [{id: 'employee_id', label: 'Employee ID'}, {id: 'hours', label: 'Hours', type: 'number'}, {id: 'date', label: 'Date', type: 'date'}] },
    'notifications': { title: 'Notification', fields: [{id: 'title', label: 'Title'}, {id: 'message', label: 'Message'}] },
    'reports': { title: 'Report', fields: [{id: 'name', label: 'Report Name'}, {id: 'type', label: 'Type', type: 'select', options: ['sales', 'inventory', 'financial', 'hr']}] },
    'logs': { title: 'Log Entry', fields: [{id: 'action', label: 'Action'}, {id: 'user_id', label: 'User ID'}] },
    'settings': { title: 'Setting', fields: [{id: 'key', label: 'Setting Key'}, {id: 'value', label: 'Value'}] }
};

window.openCreateModal = function(viewKey) {
    // Redirect to dedicated create page
    window.location.href = `/create/${viewKey}`;
};

// Close Modal Helper
window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
};

// Tool Submit Handlers
const initToolHandlers = () => {
    const stockForm = document.getElementById('stock-form');
    if (stockForm) {
        stockForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            try {
                const res = await fetch(`${API_BASE}/inventory/movement`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data)});
                if(res.ok) { alert('Stock updated!'); window.location.href='/inventory'; } else { alert('Error updating stock'); }
            } catch(e) { alert('Error'); }
        });
    }

    const expenseForm = document.getElementById('expense-form');
    if (expenseForm) {
        expenseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            try {
                const res = await fetch(`${API_BASE}/expenses`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data)});
                if(res.ok) { alert('Expense logged!'); window.location.href='/expenses'; } else { alert('Error logging expense'); }
            } catch(e) { alert('Error'); }
        });
    }
};

initToolHandlers();

window.openEditModal = async function(viewKey, id) {
    const schema = VIEW_SCHEMAS[viewKey] || { title: viewKey, fields: [{id: 'name', label: 'Name'}] };
    let endpoint = API_ENDPOINT.replace(/\/stats$/, '').split('?')[0];
    
    try {
        const item = await fetchData(`${endpoint}/${id}`);
        if (!item) return;

        const modal = document.getElementById('create-modal');
        const title = document.getElementById('modal-title');
        const fieldsContainer = document.getElementById('modal-fields');
        const form = document.getElementById('dynamic-create-form');

        title.textContent = `Edit ${schema.title}`;
        fieldsContainer.innerHTML = schema.fields.map(f => `
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">${f.label}</label>
                ${f.type === 'select' ? `
                    <select name="${f.id}" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500">
                        ${f.options.map(o => `<option value="${o}" ${item[f.id] === o ? 'selected' : ''}>${o.replace(/_/g, ' ')}</option>`).join('')}
                    </select>
                ` : `
                    <input type="${f.type || 'text'}" name="${f.id}" value="${item[f.id] || ''}" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500" required>
                `}
            </div>
        `).join('');

        modal.classList.remove('hidden');
        modal.classList.add('flex');

        form.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const body = Object.fromEntries(formData.entries());
            try {
                const response = await fetch(`${API_BASE}${endpoint}/${id}`, {
                    method: 'PUT',
                    headers: getHeaders(),
                    body: JSON.stringify(body)
                });
                if (response.ok) {
                    alert('Updated successfully!');
                    window.location.reload();
                } else {
                    const err = await response.json();
                    alert('Error: ' + (err.error || 'Failed to update'));
                }
            } catch (err) { alert('Connection error'); }
        };
    } catch (e) { alert('Error fetching item'); }
};

window.deleteRecord = async function(viewKey, id) {
    if (!confirm('Are you sure you want to delete this record?')) return;
    let endpoint = API_ENDPOINT.replace(/\/stats$/, '').split('?')[0];
    try {
        const response = await fetch(`${API_BASE}${endpoint}/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        if (response.ok) {
            alert('Deleted successfully!');
            window.location.reload();
        } else {
            const err = await response.json();
            alert('Error: ' + (err.error || 'Failed to delete'));
        }
    } catch (err) { alert('Connection error'); }
};

// Generic Open Modal (for Tools page etc)
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

async function initProfile() {
    if (document.getElementById('profile-container')) {
        try {
            const user = await fetchData('/auth/me');
            if (user) renderProfile(user);
        } catch(e) { console.error(e); }
    }
}
document.addEventListener('DOMContentLoaded', initProfile);


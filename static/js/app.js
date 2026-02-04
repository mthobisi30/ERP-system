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
                <button class="mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm" onclick="alert('Create feature coming soon!')">
                    <i class="fas fa-plus mr-2"></i> Create New
                </button>
            </div>`;
        return;
    }

    const firstItem = list[0];
    const columns = Object.keys(firstItem).slice(0, 5);
    
    // Header Generation
    const headers = columns.map(c => 
        `<th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">${c.replace(/_/g, ' ')}</th>`
    ).join('');
    
    // Row Generation
    const rows = list.map(item => {
        const cells = columns.map(col => {
            let val = item[col];
            if (val === null || val === undefined) val = '-';
            if (typeof val === 'object') val = JSON.stringify(val).substring(0, 20) + '...';
            
            // Status Badges (Simple heuristics)
            if (col.includes('status')) {
                const color = val === 'active' || val === 'completed' ? 'green' : 
                             val === 'pending' || val === 'draft' ? 'yellow' : 'gray';
                val = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800 capitalize">${val}</span>`;
            }
            
            return `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${val}</td>`;
        }).join('');
        return `<tr class="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0">${cells}</tr>`;
    }).join('');

    container.innerHTML = `
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
             <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                    <p class="text-sm text-gray-500">Managing ${list.length} records</p>
                </div>
                <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm text-sm font-medium" onclick="alert('Create feature coming soon!')">
                    <i class="fas fa-plus mr-2"></i> Add New
                </button>
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

// Minimal Dashboard Render (NO STATS CARDS)
function renderDashboard(data) {
    const container = document.getElementById('dashboard-container');
    if (!container) return;
    
    // Simple welcome message instead of cards
    container.innerHTML = `
        <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">Welcome back, Admin! 👋</h2>
            <p class="text-gray-500">Here is what's happening with your business today.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Recent Projects Preview -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 font-semibold text-gray-700 flex justify-between items-center">
                    <span>Recent Projects</span>
                    <a href="/projects" class="text-primary-600 text-sm hover:underline">View All</a>
                </div>
                <div class="p-6 text-center text-gray-500 text-sm">
                    No recent activity driven by API yet.
                </div>
            </div>

            <!-- Recent Tasks Preview -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 font-semibold text-gray-700 flex justify-between items-center">
                    <span>Pending Tasks</span>
                     <a href="/tasks" class="text-primary-600 text-sm hover:underline">View All</a>
                </div>
                 <div class="p-6 text-center text-gray-500 text-sm">
                    No pending tasks found.
                </div>
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
        const container = document.getElementById('content-area') || document.getElementById('dashboard-container') || document.getElementById('list-container');
        if(container) container.innerHTML = '<div class="flex justify-center items-center h-64"><i class="fas fa-circle-notch fa-spin text-primary-500 text-3xl"></i></div>';

        const data = await fetchData(API_ENDPOINT);
        if (data) {
            // Check context
            if (window.location.pathname === '/dashboard') {
                renderDashboard(data);
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
});

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
async function handleCreateInvoice(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        invoice_number: 'INV-' + Date.now().toString().slice(-6),
        client_id: 1, // Mock ID for now, naturally would be a select
        issue_date: new Date().toISOString().split('T')[0],
        due_date: formData.get('due_date'),
        status: 'draft',
        total_amount: 0, // Should be calculated
        items: [] // Logic to parse items needs to be implemented
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
    const data = {
        quotation_number: 'Q-' + Date.now().toString().slice(-6),
        client_id: 1, // Mock
        valid_until: formData.get('valid_until'),
        status: 'draft',
        total_amount: 0
    };

    try {
        const response = await fetch(`${API_BASE}/sales/quotations`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if(response.ok) {
            alert('Quotation created successfully!');
            window.location.href = '/quotations'; // Frontend route needs mapping
        } else {
            alert('Failed to create quotation');
        }
    } catch(err) {
        console.error(err);
        alert('Error creating quotation');
    }
}

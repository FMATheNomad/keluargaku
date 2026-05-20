/* ===================== KELUARGAKU - CLIENT-SIDE LOGIC ===================== */

const API_BASE = '/api';

// ======================== NAVIGASI ========================
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('d-none', p.id !== pageId);
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (pageId === 'dashboard') loadDashboard();
    else if (pageId === 'tasks') loadTasks();
    else if (pageId === 'stickyNotes') loadStickyNotes();
    else if (pageId === 'finance') loadTransactions();
    else if (pageId === 'emergencyContacts') loadContacts();
    else if (pageId === 'shoppingList') loadShoppingList();
    else if (pageId === 'announcements') loadAnnouncements();
    else if (pageId === 'familySettings') loadFamilyMembers();
    else if (pageId === 'annualEvents') loadEvents();
}

// ======================== API HELPER ========================
async function apiFetch(url, options = {}) {
    try {
        const res = await fetch(API_BASE + url, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('API Error:', err);
        return null;
    }
}

// ======================== FLATPICKR INIT ========================
document.addEventListener('DOMContentLoaded', function () {
    showPage('dashboard');
    document.getElementById('footerYear').textContent = new Date().getFullYear();

    flatpickr('#taskDate', { enableTime: true, dateFormat: 'Y-m-d H:i', altInput: true, altFormat: 'l, d F Y, H:i', time_24hr: true, locale: 'id' });
    flatpickr('#financeDate', { enableTime: true, dateFormat: 'Y-m-d H:i', altInput: true, altFormat: 'l, d F Y, H:i', time_24hr: true, locale: 'id' });
    flatpickr('#eventDate', { dateFormat: 'Y-m-d', altInput: true, altFormat: 'l, d F Y', locale: 'id' });
});

// ======================== TASK PROGRESS SLIDER ========================
document.addEventListener('DOMContentLoaded', function () {
    const range = document.getElementById('taskProgress');
    const label = document.getElementById('taskProgressLabel');
    if (range && label) {
        range.addEventListener('input', function () {
            const v = parseInt(this.value);
            const status = v === 0 ? 'Belum Dikerjakan' :
                           v < 50 ? 'Masih dalam Proses' :
                           v < 100 ? 'Sedang Dikerjakan' : 'Sudah Dikerjakan';
            label.textContent = `${status} (${v}%)`;
        });
    }
});

// ======================== OTHER OPTION HANDLER ========================
function handleOtherOption(select, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (select.value === 'other') {
        container.classList.remove('d-none');
    } else {
        container.classList.add('d-none');
    }
}

// ======================== FINANCE TYPE DROPDOWN ========================
document.addEventListener('DOMContentLoaded', function () {
    const menu = document.getElementById('financeTypeMenu');
    if (menu) {
        menu.addEventListener('click', function (e) {
            const item = e.target.closest('.dropdown-item');
            if (!item) return;
            e.preventDefault();
            document.getElementById('financeType').value = item.dataset.value;
            menu.closest('.input-group').querySelector('.dropdown-toggle').textContent = item.dataset.value;
        });
    }
});

// ======================== DASHBOARD ========================
async function loadDashboard() {
    const data = await apiFetch('/dashboard');
    if (!data) return;
    const stats = [
        { label: 'Tugas', count: data.tasks || 0, icon: '📋' },
        { label: 'Selesai', count: data.tasks_completed || 0, icon: '✅' },
        { label: 'Catatan', count: data.sticky_notes || 0, icon: '📝' },
        { label: 'Transaksi', count: data.transactions || 0, icon: '💰' },
        { label: 'Kontak', count: data.contacts || 0, icon: '📞' },
        { label: 'Belanja', count: data.shopping_items || 0, icon: '🛒' },
        { label: 'Anggota', count: data.family_members || 0, icon: '👨‍👩‍👧‍👦' },
        { label: 'Acara', count: data.events || 0, icon: '🎉' },
    ];
    document.getElementById('dashboardStats').innerHTML = stats.map(s =>
        `<div class="col-6 col-md-3"><div class="stat-card"><div class="stat-number">${s.icon} ${s.count}</div><div class="stat-label">${s.label}</div></div></div>`
    ).join('');

    const tasksEl = document.getElementById('recentTasks');
    if (data.recent_tasks && data.recent_tasks.length) {
        tasksEl.innerHTML = data.recent_tasks.map(t =>
            `<div class="task-item ${t.progress === 100 ? 'completed' : ''}"><strong>${escHtml(t.title)}</strong> <span class="badge bg-secondary badge-progress">${t.progress}%</span></div>`
        ).join('');
    } else {
        tasksEl.innerHTML = '<p class="text-muted">Belum ada tugas.</p>';
    }

    const annEl = document.getElementById('recentAnnouncements');
    if (data.recent_announcements && data.recent_announcements.length) {
        annEl.innerHTML = data.recent_announcements.map(a =>
            `<div class="announcement-item announcement-normal"><strong>${escHtml(a.title)}</strong><br /><small class="text-muted">${a.created_at || ''}</small></div>`
        ).join('');
    } else {
        annEl.innerHTML = '<p class="text-muted">Belum ada pengumuman.</p>';
    }
}

// ======================== TASKS ========================
async function loadTasks() {
    const tasks = await apiFetch('/tasks');
    const el = document.getElementById('taskList');
    if (!tasks || !tasks.length) {
        el.innerHTML = '<div class="empty-state">Belum ada tugas. Buat tugas baru di atas!</div>';
        return;
    }
    el.innerHTML = tasks.map(t =>
        `<div class="task-item ${t.progress === 100 ? 'completed' : ''}">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${escHtml(t.title)}</strong>
                    ${t.assignee ? `<span class="badge bg-info ms-1">${escHtml(t.assignee)}</span>` : ''}
                    ${t.location ? `<br /><small class="text-muted">📍 ${escHtml(t.location)}</small>` : ''}
                    ${t.due_date ? `<br /><small class="text-muted">📅 ${escHtml(t.due_date)}</small>` : ''}
                    ${t.notes ? `<br /><small>${escHtml(t.notes)}</small>` : ''}
                </div>
                <div class="text-end">
                    <span class="badge ${t.progress === 100 ? 'bg-success' : 'bg-secondary'} badge-progress">${t.progress}%</span>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="deleteTask(${t.id})">✕</button>
                </div>
            </div>
        </div>`
    ).join('');
}

async function deleteTask(id) {
    await apiFetch(`/tasks/${id}`, { method: 'DELETE' });
    loadTasks();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('taskForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const assigneeSelect = document.getElementById('taskAssignee');
            let assignee = assigneeSelect.value;
            if (assignee === 'other') {
                assignee = document.getElementById('taskOtherInput').value || 'Lainnya';
            }
            await apiFetch('/tasks', {
                method: 'POST',
                body: JSON.stringify({
                    title: document.getElementById('taskTitle').value,
                    location: document.getElementById('taskLocation').value,
                    assignee: assignee,
                    due_date: document.getElementById('taskDate').value,
                    progress: parseInt(document.getElementById('taskProgress').value),
                    notes: document.getElementById('taskNotes').value,
                })
            });
            form.reset();
            loadTasks();
        });
    }
});

// ======================== STICKY NOTES ========================
async function loadStickyNotes() {
    const notes = await apiFetch('/sticky-notes');
    const el = document.getElementById('stickyList');
    if (!notes || !notes.length) {
        el.innerHTML = '<div class="col-12"><div class="empty-state">Belum ada catatan.</div></div>';
        return;
    }
    el.innerHTML = notes.map(n =>
        `<div class="col-md-4 mb-3">
            <div class="sticky-note-card">
                ${escHtml(n.content)}
                <button class="btn-close" onclick="deleteSticky(${n.id})" aria-label="Hapus"></button>
            </div>
        </div>`
    ).join('');
}

async function deleteSticky(id) {
    await apiFetch(`/sticky-notes/${id}`, { method: 'DELETE' });
    loadStickyNotes();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('stickyForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const content = document.getElementById('stickyContent').value.trim();
            if (!content) return;
            await apiFetch('/sticky-notes', {
                method: 'POST',
                body: JSON.stringify({ content })
            });
            form.reset();
            loadStickyNotes();
        });
    }
});

// ======================== FINANCE ========================
async function loadTransactions() {
    const txns = await apiFetch('/transactions');
    const el = document.getElementById('transactionList');
    if (!txns || !txns.length) {
        el.innerHTML = '<div class="empty-state">Belum ada transaksi.</div>';
        return;
    }
    el.innerHTML = txns.map(t =>
        `<div class="transaction-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${t.type}</strong> — Rp${Number(t.amount).toLocaleString('id-ID')}
                    ${t.category ? `<span class="badge bg-secondary">${escHtml(t.category)}</span>` : ''}
                    ${t.asset ? `<small class="text-muted ms-1">${escHtml(t.asset)}</small>` : ''}
                    ${t.transaction_date ? `<br /><small class="text-muted">📅 ${escHtml(t.transaction_date)}</small>` : ''}
                    ${t.notes ? `<br /><small>${escHtml(t.notes)}</small>` : ''}
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction(${t.id})">✕</button>
            </div>
        </div>`
    ).join('');
}

async function deleteTransaction(id) {
    await apiFetch(`/transactions/${id}`, { method: 'DELETE' });
    loadTransactions();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('financeForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            await apiFetch('/transactions', {
                method: 'POST',
                body: JSON.stringify({
                    amount: parseFloat(document.getElementById('financeAmount').value) || 0,
                    type: document.getElementById('financeType').value,
                    category: document.getElementById('financeCategory').value,
                    asset: document.getElementById('financeAsset').value,
                    notes: document.getElementById('financeNotes').value,
                    transaction_date: document.getElementById('financeDate').value,
                })
            });
            form.reset();
            document.querySelector('#financeForm .dropdown-toggle').textContent = 'Jenis';
            loadTransactions();
        });
    }
});

// ======================== EMERGENCY CONTACTS ========================
async function loadContacts() {
    const contacts = await apiFetch('/emergency-contacts');
    const el = document.getElementById('contactList');
    if (!contacts || !contacts.length) {
        el.innerHTML = '<div class="empty-state">Belum ada kontak darurat.</div>';
        return;
    }
    el.innerHTML = contacts.map(c =>
        `<div class="contact-item d-flex justify-content-between align-items-center">
            <div>
                <strong>${escHtml(c.name)}</strong>
                <br /><small class="text-muted">${escHtml(c.phone_code)} ${escHtml(c.phone_number)}</small>
            </div>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteContact(${c.id})">✕</button>
        </div>`
    ).join('');
}

async function deleteContact(id) {
    await apiFetch(`/emergency-contacts/${id}`, { method: 'DELETE' });
    loadContacts();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const name = document.getElementById('contactName').value.trim();
            const phone = document.getElementById('contactPhone').value.trim();
            if (!name || !phone) return;
            await apiFetch('/emergency-contacts', {
                method: 'POST',
                body: JSON.stringify({
                    name,
                    phone_code: document.getElementById('contactCode').value,
                    phone_number: phone,
                })
            });
            form.reset();
            loadContacts();
        });
    }
});

// ======================== SHOPPING LIST ========================
let shoppingFieldsContainer, shoppingFieldSelect, shoppingCustomCount, shoppingAddFields;

function addInputFields(count) {
    for (let i = 0; i < count; i++) {
        const div = document.createElement('div');
        div.className = 'input-group mb-1';
        div.innerHTML = `
            <input type="text" class="form-control" placeholder="Nama barang" name="itemName" required />
            <input type="text" class="form-control" placeholder="Jumlah" name="itemQuantity" style="max-width:120px" />
            <button type="submit" class="btn btn-primary">+</button>
        `;
        shoppingFieldsContainer.appendChild(div);
    }
}

async function loadShoppingList() {
    const items = await apiFetch('/shopping-items');
    const el = document.getElementById('shoppingListItems');
    if (!items || !items.length) {
        el.innerHTML = '<div class="empty-state">Belum ada barang belanjaan.</div>';
        return;
    }
    el.innerHTML = items.map(i =>
        `<div class="item-row">
            <span><strong>${escHtml(i.item_name)}</strong> × ${escHtml(i.quantity)}</span>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteShoppingItem(${i.id})">✕</button>
        </div>`
    ).join('');
}

async function deleteShoppingItem(id) {
    await apiFetch(`/shopping-items/${id}`, { method: 'DELETE' });
    loadShoppingList();
}

document.addEventListener('DOMContentLoaded', function () {
    shoppingFieldsContainer = document.getElementById('shoppingFieldsContainer');
    shoppingFieldSelect = document.getElementById('shoppingFieldSelect');
    shoppingCustomCount = document.getElementById('shoppingCustomCount');
    shoppingAddFields = document.getElementById('shoppingAddFields');

    if (shoppingAddFields) {
        shoppingAddFields.addEventListener('click', function (e) {
            e.preventDefault();
            const selected = parseInt(shoppingFieldSelect.value) || 1;
            const custom = parseInt(shoppingCustomCount.value);
            const count = custom || selected;
            addInputFields(count);
        });
    }

    const form = document.getElementById('shoppingForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const names = form.querySelectorAll('input[name="itemName"]');
            const quants = form.querySelectorAll('input[name="itemQuantity"]');
            for (let i = 0; i < names.length; i++) {
                const name = names[i].value.trim();
                if (!name) continue;
                await apiFetch('/shopping-items', {
                    method: 'POST',
                    body: JSON.stringify({
                        item_name: name,
                        quantity: quants[i]?.value || '1',
                    })
                });
            }
            shoppingFieldsContainer.innerHTML = `
                <div class="input-group mb-1">
                    <input type="text" class="form-control" placeholder="Nama barang" name="itemName" required />
                    <input type="text" class="form-control" placeholder="Jumlah" name="itemQuantity" style="max-width:120px" />
                    <button type="submit" class="btn btn-primary">+</button>
                </div>`;
            loadShoppingList();
        });
    }
});

// ======================== ANNOUNCEMENTS ========================
async function loadAnnouncements() {
    const anns = await apiFetch('/announcements');
    const el = document.getElementById('announcementList');
    if (!anns || !anns.length) {
        el.innerHTML = '<div class="empty-state">Belum ada pengumuman.</div>';
        return;
    }
    el.innerHTML = anns.map(a =>
        `<div class="announcement-item ${a.priority === 'urgent' || a.priority === 'tinggi' ? 'announcement-high' : 'announcement-normal'}">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${escHtml(a.title)}</strong>
                    ${a.priority === 'urgent' ? '<span class="badge bg-danger ms-1">URGENT</span>' : a.priority === 'tinggi' ? '<span class="badge bg-warning ms-1">Penting</span>' : ''}
                    ${a.content ? `<br /><small>${escHtml(a.content)}</small>` : ''}
                    <br /><small class="text-muted">${a.created_at || ''}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteAnnouncement(${a.id})">✕</button>
            </div>
        </div>`
    ).join('');
}

async function deleteAnnouncement(id) {
    await apiFetch(`/announcements/${id}`, { method: 'DELETE' });
    loadAnnouncements();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('announcementForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            await apiFetch('/announcements', {
                method: 'POST',
                body: JSON.stringify({
                    title: document.getElementById('announcementTitle').value,
                    content: document.getElementById('announcementContent').value,
                    priority: document.getElementById('announcementPriority').value,
                })
            });
            form.reset();
            loadAnnouncements();
        });
    }
});

// ======================== FAMILY MEMBERS ========================
async function loadFamilyMembers() {
    const members = await apiFetch('/family-members');
    const el = document.getElementById('familyList');
    if (!members || !members.length) {
        el.innerHTML = '<div class="empty-state">Belum ada anggota keluarga.</div>';
        return;
    }
    el.innerHTML = members.map(m =>
        `<div class="contact-item d-flex justify-content-between align-items-center">
            <div>
                <strong>${escHtml(m.name)}</strong>
                ${m.role ? `<span class="badge bg-secondary ms-1">${escHtml(m.role)}</span>` : ''}
            </div>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteFamilyMember(${m.id})">✕</button>
        </div>`
    ).join('');
}

async function deleteFamilyMember(id) {
    await apiFetch(`/family-members/${id}`, { method: 'DELETE' });
    loadFamilyMembers();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('familyForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const name = document.getElementById('familyName').value.trim();
            if (!name) return;
            await apiFetch('/family-members', {
                method: 'POST',
                body: JSON.stringify({
                    name,
                    role: document.getElementById('familyRole').value,
                })
            });
            form.reset();
            loadFamilyMembers();
        });
    }
});

// ======================== ANNUAL EVENTS ========================
async function loadEvents() {
    const events = await apiFetch('/annual-events');
    const el = document.getElementById('eventList');
    if (!events || !events.length) {
        el.innerHTML = '<div class="empty-state">Belum ada acara tahunan.</div>';
        return;
    }
    el.innerHTML = events.map(e =>
        `<div class="event-item d-flex justify-content-between align-items-start">
            <div>
                <strong>${escHtml(e.name)}</strong>
                ${e.event_date ? `<br /><small class="text-muted">📅 ${escHtml(e.event_date)}</small>` : ''}
                ${e.notes ? `<br /><small>${escHtml(e.notes)}</small>` : ''}
            </div>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteEvent(${e.id})">✕</button>
        </div>`
    ).join('');
}

async function deleteEvent(id) {
    await apiFetch(`/annual-events/${id}`, { method: 'DELETE' });
    loadEvents();
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('eventForm');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            await apiFetch('/annual-events', {
                method: 'POST',
                body: JSON.stringify({
                    name: document.getElementById('eventName').value,
                    event_date: document.getElementById('eventDate').value,
                    notes: document.getElementById('eventNotes').value,
                })
            });
            form.reset();
            loadEvents();
        });
    }
});

// ======================== HELPER ========================
function escHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

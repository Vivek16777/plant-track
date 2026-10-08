// Theme Management
const storageKey = 'theme-preference';

const getColorPreference = () => {
    if (localStorage.getItem(storageKey)) {
        return localStorage.getItem(storageKey);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const setPreference = (theme) => {
    localStorage.setItem(storageKey, theme);
    reflectPreference(theme);
};

const reflectPreference = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
};

// Initialize Theme
reflectPreference(getColorPreference());

document.addEventListener('DOMContentLoaded', () => {
    // Reflect preference immediately on DOM load to ensure toggle elements exist
    reflectPreference(getColorPreference());

    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const currentTheme = getColorPreference();
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setPreference(nextTheme);
        });
    }

    // Toggle Sidebar in mobile
    const toggleSidebar = document.getElementById('toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    if (toggleSidebar && sidebar) {
        toggleSidebar.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('active')) {
            if (!sidebar.contains(e.target) && !toggleSidebar.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
});

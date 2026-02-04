// Clawdi's Tagebuch - App Logic

const ENTRIES_INDEX = 'entries/index.json';
let entries = [];
let currentIndex = 0;

async function init() {
    try {
        const response = await fetch(ENTRIES_INDEX);
        if (!response.ok) throw new Error('Index nicht gefunden');
        
        entries = await response.json();
        entries.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        if (entries.length > 0) {
            await showEntry(0);
            updateNav();
        } else {
            showNoEntries();
        }
    } catch (error) {
        console.error('Fehler beim Laden:', error);
        showNoEntries();
    }
}

async function showEntry(index) {
    const content = document.getElementById('diary-content');
    const dateDisplay = document.getElementById('current-date');
    
    if (index < 0 || index >= entries.length) return;
    
    currentIndex = index;
    const entry = entries[index];
    
    try {
        const response = await fetch(`entries/${entry.file}`);
        if (!response.ok) throw new Error('Eintrag nicht gefunden');
        
        const markdown = await response.text();
        content.innerHTML = `<div class="diary-entry">${marked.parse(markdown)}</div>`;
        dateDisplay.textContent = formatDate(entry.date);
    } catch (error) {
        content.innerHTML = `<div class="no-entry">Eintrag konnte nicht geladen werden 😅</div>`;
    }
    
    updateNav();
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('de-DE', options);
}

function updateNav() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    prevBtn.disabled = currentIndex >= entries.length - 1;
    nextBtn.disabled = currentIndex <= 0;
}

function showNoEntries() {
    const content = document.getElementById('diary-content');
    const dateDisplay = document.getElementById('current-date');
    
    content.innerHTML = `
        <div class="no-entry">
            <p>Noch keine Einträge vorhanden! 📝</p>
            <p>Bald gibt's hier was zu lesen...</p>
        </div>
    `;
    dateDisplay.textContent = '---';
}

// Event Listeners
document.getElementById('prev-btn').addEventListener('click', () => {
    if (currentIndex < entries.length - 1) {
        showEntry(currentIndex + 1);
    }
});

document.getElementById('next-btn').addEventListener('click', () => {
    if (currentIndex > 0) {
        showEntry(currentIndex - 1);
    }
});

// Start
init();

let badgesData = {};
let usersList = [];

// Fetch badges data
async function fetchBadges() {
    try {
        const response = await fetch('../badges.json');
        badgesData = await response.json();
        usersList = Object.values(badgesData).map(badge => badge.username);
        setupAutocomplete();
    } catch (error) {
        console.error('Error loading badges:', error);
    }
}

// Setup autocomplete
function setupAutocomplete() {
    const input = document.getElementById('username');
    let currentFocus;

    input.addEventListener('input', function(e) {
        let val = this.value;
        closeAllLists();
        if (!val) return false;
        currentFocus = -1;

        const suggestionList = document.createElement('div');
        suggestionList.setAttribute('id', this.id + 'autocomplete-list');
        suggestionList.setAttribute('class', 'autocomplete-items list-group position-absolute w-100');
        this.parentNode.appendChild(suggestionList);

        usersList.forEach(username => {
            if (username.toLowerCase().includes(val.toLowerCase())) {
                const item = document.createElement('div');
                item.setAttribute('class', 'list-group-item list-group-item-action');
                item.innerHTML = username;
                item.addEventListener('click', function(e) {
                    input.value = username;
                    generateBadge(username);
                    closeAllLists();
                });
                suggestionList.appendChild(item);
            }
        });
    });

    function closeAllLists(elmnt) {
        const x = document.getElementsByClassName('autocomplete-items');
        for (let i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != input) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    document.addEventListener('click', function (e) {
        closeAllLists(e.target);
    });
}

// Generate badge
function generateBadge(username) {
    const badgeKey = Object.keys(badgesData).find(key => 
        badgesData[key].username === username
    );

    if (!badgeKey) return;

    const badge = badgesData[badgeKey];
    const style = document.getElementById('badgeStyle').value;
    const color = document.getElementById('badgeColor').value.substring(1); // Remove # from hex color

    const badgeUrl = `https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsilvermete0r%2Fdeepml-top%2Fmain%2Fbadges.json&query=%24.${badgeKey}.label&prefix=Rank%20&style=${style}&label=%F0%9F%9A%80%20DeepML&color=${color}&link=https%3A%2F%2Fwww.deep-ml.com%2Fleaderboard`;

    const markdownCode = `![DeepML ${username}](${badgeUrl})`;
    const htmlCode = `<img src="${badgeUrl}" alt="DeepML ${username}">`;

    document.getElementById('previewArea').innerHTML = `<img src="${badgeUrl}" alt="DeepML ${username}">`;
    document.getElementById('markdownText').textContent = markdownCode;
    document.getElementById('htmlText').textContent = htmlCode;

    document.getElementById('badgePreview').style.display = 'block';
    document.getElementById('markdownCode').style.display = 'block';
    document.getElementById('htmlCode').style.display = 'block';
}

// Add event listeners for style changes
document.getElementById('badgeStyle').addEventListener('change', () => {
    const username = document.getElementById('username').value;
    if (username) generateBadge(username);
});

document.getElementById('badgeColor').addEventListener('input', () => {
    const username = document.getElementById('username').value;
    if (username) generateBadge(username);
});

// Copy code function
function copyCode(type) {
    const element = document.getElementById(`${type}Text`);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = element.parentElement.querySelector('.copy-btn');
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = 'Copy', 2000);
    });
}

// Initialize
fetchBadges();

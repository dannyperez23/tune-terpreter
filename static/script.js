document.addEventListener('DOMContentLoaded', function() {
    const themeButton = document.getElementById('theme_button');
    const songSearchBox = document.getElementById('song_search_box');
    const artistSearchBox = document.getElementById('artist_search_box');
    const searchForm = document.getElementById('search_form');
    const errorDisplay = document.getElementById('error_display');
    const loadingDisplay = document.getElementById('loading_display');
    const lyricsBox = document.getElementById('lyrics_box');
    const summaryBox = document.getElementById('summary_box');
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (savedTheme === null && prefersDark)) {
        document.documentElement.classList.add('dark');
    }

    themeButton.addEventListener('click', function() {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    searchForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const songQuery = songSearchBox.value.trim();
        const artistQuery = artistSearchBox.value.trim();

        if (songQuery === '' || artistQuery === '') {
            errorDisplay.textContent = 'Search query is incomplete. Try again!';
            errorDisplay.classList.remove('hidden');
            console.log("Search query is incomplete.");
            return;
        }

        errorDisplay.classList.add('hidden');
        errorDisplay.textContent = '';
        lyricsBox.textContent = '';
        summaryBox.textContent = '';
        
        loadingDisplay.classList.remove('hidden');
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ song: songQuery, artist: artistQuery})
            });

            const data = await response.json();

            if(!response.ok){
                throw new Error(data.error || "Request failed.");
            }
            
            lyricsBox.textContent = data.lyrics;
            summaryBox.textContent = data.summary;

        } catch (error) {
            errorDisplay.textContent = error.message;
            errorDisplay.classList.remove('hidden');
            console.error('Error: ', error);
        } finally {
            loadingDisplay.classList.add('hidden');
        }
    });

});
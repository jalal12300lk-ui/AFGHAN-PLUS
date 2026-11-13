function openPage(page) {
    const routes = {
        currency: "currency.html",
        education: "education.html",
        jobs: "jobs.html",
        market: "market.html",
        news: "news.html",
        weather: "weather.html",
        contact: "contact.html"
    };

    if (routes[page]) {
        window.location.href = routes[page];
    } else {
        alert("به افغان پلاس خوش آمدید!");
    }
}

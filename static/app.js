document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("animalSearch");
    const table = document.getElementById("animalTable");

    if (search && table) {
        search.addEventListener("input", () => {
            const term = search.value.toLowerCase().trim();
            table.querySelectorAll("tbody tr").forEach(row => {
                row.style.display = row.innerText.toLowerCase().includes(term) ? "" : "none";
            });
        });
    }

    document.querySelectorAll(".alert").forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transition = "opacity .4s";
            setTimeout(() => alert.remove(), 450);
        }, 4500);
    });
});


const fields = ["toman", "usd", "eur"];

function loadRates() {
    fields.forEach(id => {
        const value = localStorage.getItem(id);
        if (value !== null) {
            document.getElementById(id).value = value;
        }
    });
}

function saveRates() {
    fields.forEach(id => {
        localStorage.setItem(
            id,
            document.getElementById(id).value
        );
    });

    document.getElementById("status").innerText =
        "✅ نرخ‌ها با موفقیت ذخیره شدند.";
}

function convert() {
    const amount = Number(
        document.getElementById("amount").value
    );

    const toman = Number(
        document.getElementById("toman").value
    );

    const usd = Number(
        document.getElementById("usd").value
    );

    const eur = Number(
        document.getElementById("eur").value
    );

    const result = document.getElementById("result");

    if (!Number.isFinite(amount) || amount <= 0) {
        result.innerText = "لطفاً مقدار افغانی را وارد کن.";
        return;
    }

    if (
        !Number.isFinite(toman) || toman <= 0 ||
        !Number.isFinite(usd) || usd <= 0 ||
        !Number.isFinite(eur) || eur <= 0
    ) {
        result.innerText =
            "لطفاً ابتدا نرخ معتبر هر سه ارز را وارد و ذخیره کن.";
        return;
    }

    result.innerHTML = `
        🇦🇫 ${amount.toLocaleString()} افغانی
        <hr>
        🇮🇷 ${(amount * toman).toLocaleString("en-US", {
            maximumFractionDigits: 2
        })} تومان
        <hr>
        🇺🇸 ${(amount * usd).toLocaleString("en-US", {
            maximumFractionDigits: 4
        })} دلار
        <hr>
        🇪🇺 ${(amount * eur).toLocaleString("en-US", {
            maximumFractionDigits: 4
        })} یورو
    `;
}

loadRates();


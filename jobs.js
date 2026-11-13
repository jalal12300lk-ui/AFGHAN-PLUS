
let jobs = JSON.parse(localStorage.getItem("afghan_jobs") || "[]");

function saveJobs(){
    localStorage.setItem("afghan_jobs",JSON.stringify(jobs));
}

function toggleForm(){
    const form=document.getElementById("form");
    form.style.display=form.style.display==="block"?"none":"block";
}

function addJob(){

    const title=document.getElementById("jobTitle").value.trim();
    const company=document.getElementById("company").value.trim();
    const city=document.getElementById("city").value;
    const type=document.getElementById("type").value;
    const description=document.getElementById("description").value.trim();

    if(!title || !company || !city || !description){
        alert("لطفاً تمام قسمت‌ها را تکمیل کنید.");
        return;
    }

    const job={
        id:Date.now(),
        title,
        company,
        city,
        type,
        description
    };

    jobs.unshift(job);
    saveJobs();

    renderJobs();

    document.getElementById("jobTitle").value="";
    document.getElementById("company").value="";
    document.getElementById("city").value="";
    document.getElementById("description").value="";

    toggleForm();

    alert("آگهی در این دستگاه ذخیره شد.");
}

function renderJobs(){

    const search=document.getElementById("search").value.toLowerCase();
    const province=document.getElementById("province").value;

    const list=document.getElementById("jobsList");

    const filtered=jobs.filter(job=>
        (job.title+" "+job.company+" "+job.description).toLowerCase().includes(search)
        && (!province || job.city===province)
    );

    list.innerHTML="";

    if(filtered.length===0){
        list.innerHTML="<p>هیچ آگهی‌ای پیدا نشد.</p>";
        return;
    }

    filtered.forEach(job=>{

        const card=document.createElement("div");
        card.className="job";

        const title=document.createElement("h3");
        title.textContent="💼 "+job.title;

        const company=document.createElement("p");
        company.textContent="🏢 "+job.company;

        const city=document.createElement("p");
        city.textContent="📍 "+job.city;

        const type=document.createElement("span");
        type.className="badge";
        type.textContent=job.type;

        const description=document.createElement("p");
        description.textContent=job.description;

        card.append(title,company,city,type,description);
        list.appendChild(card);
    });
}

document.getElementById("search").addEventListener("input",renderJobs);
document.getElementById("province").addEventListener("change",renderJobs);

renderJobs();


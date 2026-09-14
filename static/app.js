const list = document.querySelector("#task-list");
const form = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const count = document.querySelector("#task-count");
const message = document.querySelector("#message");
const template = document.querySelector("#task-template");

function showMessage(text = "") {
  message.textContent = text;
}

async function request(url, options) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || "Something went wrong.");
  }

  return response.status === 204 ? null : response.json();
}

function render(tasks) {
  list.replaceChildren();

  tasks.forEach((task) => {
    const item = template.content.firstElementChild.cloneNode(true);
    const toggle = item.querySelector(".toggle");

    item.querySelector(".title").textContent = task.title;
    toggle.checked = task.completed;
    item.classList.toggle("done", task.completed);

    toggle.addEventListener("change", async () => {
      try {
        await request(`/api/tasks/${task.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ completed: toggle.checked }),
        });

        loadTasks();
      } catch (error) {
        showMessage(error.message);
        toggle.checked = !toggle.checked;
      }
    });

    item.querySelector(".delete").addEventListener("click", async () => {
      try {
        await request(`/api/tasks/${task.id}`, { method: "DELETE" });
        loadTasks();
      } catch (error) {
        showMessage(error.message);
      }
    });

    list.append(item);
  });

  const remaining = tasks.filter((task) => !task.completed).length;
  count.textContent = `${remaining} remaining`;
}

async function loadTasks() {
  try {
    showMessage();
    render(await request("/api/tasks"));
  } catch (error) {
    showMessage(`Could not load tasks: ${error.message}`);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    await request("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: titleInput.value }),
    });

    titleInput.value = "";
    loadTasks();
  } catch (error) {
    showMessage(error.message);
  }
});

loadTasks();
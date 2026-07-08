document.addEventListener("DOMContentLoaded", function () {
  const addBtn = document.getElementById("add-btn");
  const todoInput = document.getElementById("todo-input");
  const todoList = document.getElementById("todo-list");

  // Function to add a new TODO item
  addBtn.addEventListener("click", function () {
    if (todoInput.value.trim()) {
      const listItem = document.createElement("li");
      listItem.textContent = todoInput.value;

      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";

      delBtn.onclick = function () {
        todoList.removeChild(listItem);
      };

      listItem.appendChild(delBtn);
      todoList.appendChild(listItem);

      todoInput.value = "";
    }
  });
});

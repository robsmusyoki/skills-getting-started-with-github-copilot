document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.style.border = "1px solid #ccc";
        activityCard.style.borderRadius = "8px";
        activityCard.style.padding = "16px";
        activityCard.style.marginBottom = "20px";
        activityCard.style.background = "#f9f9f9";
        activityCard.style.boxShadow = "0 2px 6px rgba(0,0,0,0.04)";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML with delete icon and no bullet points
        let participantsHTML = "";
        if (details.participants.length > 0) {
          participantsHTML = `
            <div style="margin-top: 10px;">
              <strong>Participants:</strong>
              <ul style="margin: 6px 0 0 18px; padding: 0; list-style: none;">
                ${details.participants.map(email => `
                  <li style="margin-bottom: 2px; display: flex; align-items: center;">
                    <span style="flex:1;">${email}</span>
                    <span class="delete-participant" data-activity="${name}" data-email="${email}" title="Remove participant" style="cursor:pointer; color:#c62828; margin-left:8px; font-size:16px;">&#128465;</span>
                  </li>
                `).join("")}
              </ul>
            </div>
          `;
        } else {
          participantsHTML = `<div style="margin-top: 10px;"><strong>Participants:</strong> <em>No participants yet</em></div>`;
        }

        activityCard.innerHTML = `
          <h4 style="margin-top:0;">${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();


      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh activities after successful signup
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
  // Event delegation for delete participant icon
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-participant")) {
      const activity = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");
      if (confirm(`Remove ${email} from ${activity}?`)) {
        try {
          const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`, {
            method: "DELETE",
          });
          const result = await response.json();
          if (response.ok) {
            messageDiv.textContent = result.message || "Participant removed.";
            messageDiv.className = "success";
            fetchActivities();
          } else {
            messageDiv.textContent = result.detail || "Failed to remove participant.";
            messageDiv.className = "error";
          }
        } catch (error) {
          messageDiv.textContent = "Error removing participant.";
          messageDiv.className = "error";
        }
        messageDiv.classList.remove("hidden");
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      }
    }
  });
});

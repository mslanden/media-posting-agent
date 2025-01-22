function loadScheduledPostsJS() {
    fetch("/get_posts")
        .then((response) => response.json())
        .then((posts) => {
            const postList = document.getElementById("post-list");
            postList.innerHTML = "";
            if (posts.length === 0) {
                const listItem = document.createElement("li");
                listItem.textContent = "No scheduled posts";
                postList.appendChild(listItem);
            } else {
                posts.forEach((post) => {
                    const listItem = document.createElement("li");
                    listItem.textContent = `Tweet: ${post.tweet} Date: ${post.post_date} Time: ${post.post_time}`;
                    postList.appendChild(listItem);
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while loading scheduled posts.");
        });
}

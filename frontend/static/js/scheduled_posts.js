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
                    listItem.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p><strong>Tweet:</strong> ${post.tweet}</p>
                                <p><strong>Scheduled:</strong> ${post.post_date} ${post.post_time}</p>
                            </div>
                            <div>
                                <button style="margin-right: 5px;" onclick="editPost('${post.id}')">Edit</button>
                                <button onclick="deletePost('${post.id}')">Delete</button>
                            </div>
                        </div>
                    `;
                    postList.appendChild(listItem);
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while loading scheduled posts.");
        });
}

function editPost(postId) {
    console.log('Edit post:', postId);
    alert('Edit functionality is not implemented yet.');
}

function deletePost(postId) {
    console.log('Delete post:', postId);
    alert('Delete functionality is not implemented yet.');
}

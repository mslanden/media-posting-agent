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
    const postItem = document.querySelector(`[data-post-id="${postId}"]`);
    const postText = postItem.querySelector('p:first-child').textContent.replace('Tweet: ', '');
    const scheduledTime = postItem.querySelector('p:nth-child(2)').textContent.replace('Scheduled: ', '');
    const [scheduledDate, scheduledTimeOnly] = scheduledTime.split(' ');

    const newTweet = prompt('Edit tweet:', postText);
    if (newTweet === null) return;
    const newDate = prompt('Edit date:', scheduledDate);
    if (newDate === null) return;
    const newTime = prompt('Edit time:', scheduledTimeOnly);
    if (newTime === null) return;

    const updatedPost = {
        id: postId,
        tweet: newTweet,
        post_date: newDate,
        post_time: newTime
    };

    fetch('/update_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: postId,
            updated_post: updatedPost,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error updating post: ' + data.error);
        } else {
            alert('Post updated successfully');
            loadScheduledPostsJS();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the post.');
    });
}

function deletePost(postId) {
    if (confirm('Are you sure you want to delete this post?')) {
        fetch('/delete_post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: postId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error deleting post: ' + data.error);
            } else {
                alert('Post deleted successfully');
                loadScheduledPostsJS();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the post.');
        });
    }
}

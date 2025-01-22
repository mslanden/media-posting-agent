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
                    listItem.setAttribute('data-post-id', post.id);
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
    const tweetElement = postItem.querySelector('p:first-child');
    const scheduledElement = postItem.querySelector('p:nth-child(2)');
    const postText = tweetElement ? tweetElement.textContent.replace('Tweet: ', '') : '';
    const scheduledTime = scheduledElement ? scheduledElement.textContent.replace('Scheduled: ', '') : '';
    const [scheduledDate, scheduledTimeOnly] = scheduledTime.trim().split(' ');

    let newTweet = promptWithTextarea('Edit tweet:', postText);
    if (newTweet === null) return;
    if (newTweet.trim() === "") {
        newTweet = postText;
    }
    const newDate = prompt('Edit date:', scheduledDate);
    if (newDate === null) return;
    const newTime = prompt('Edit time:', scheduledTimeOnly);
    if (newTime === null) return;

    fetch('/update_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: postId,
            updated_post: {
                tweet: newTweet,
                post_date: newDate,
                post_time: newTime
            }
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error updating post: ' + data.error);
        } else {
            const postItem = document.querySelector(`[data-post-id="${postId}"]`);
            const tweetElement = postItem.querySelector('p:first-child');
            const scheduledElement = postItem.querySelector('p:nth-child(2)');
            if (tweetElement) {
                tweetElement.innerHTML = `<strong>Tweet:</strong> ${newTweet}`;
            }
            if (scheduledElement) {
                scheduledElement.innerHTML = `<strong>Scheduled:</strong> ${newDate} ${newTime}`;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the post.');
    });
}

function promptWithTextarea(message, defaultValue) {
    const textarea = document.createElement('textarea');
    textarea.value = defaultValue;
    textarea.style.width = '500px';
    textarea.style.height = '200px';
    textarea.style.display = 'block';
    textarea.style.margin = '10px 0';

    const dialog = document.createElement('div');
    dialog.style.position = 'fixed';
    dialog.style.top = '50%';
    dialog.style.left = '50%';
    dialog.style.transform = 'translate(-50%, -50%)';
    dialog.style.backgroundColor = 'white';
    dialog.style.padding = '20px';
    dialog.style.border = '1px solid #ccc';
    dialog.style.zIndex = '1000';

    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    dialog.appendChild(messageElement);
    dialog.appendChild(textarea);

    const okButton = document.createElement('button');
    okButton.textContent = 'OK';
    okButton.style.marginRight = '10px';
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';

    dialog.appendChild(okButton);
    dialog.appendChild(cancelButton);

    document.body.appendChild(dialog);

    return new Promise(resolve => {
        okButton.onclick = () => {
            document.body.removeChild(dialog);
            resolve(textarea.value);
        };
        cancelButton.onclick = () => {
            document.body.removeChild(dialog);
            resolve(null);
        };
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

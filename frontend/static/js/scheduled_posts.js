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
                                <p><strong>${post.media_type.charAt(0).toUpperCase() + post.media_type.slice(1)}:</strong> ${post.content}</p>
                                <p><strong>Scheduled:</strong> ${post.post_date} ${post.post_time}</p>
                                ${post.image_path ? `<img src="${post.image_path}" alt="Post Image" style="max-width: 100px; max-height: 100px;">` : ''}
                            </div>
                            </div>
                        </div>
                    `;
                    listItem.addEventListener('click', () => editPost(post.id, post.content, post.post_date, post.post_time, post.image_path, post.media_type));
                    postList.appendChild(listItem);
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while loading scheduled posts.");
        });
}

function editPost(postId, tweet, postDate, postTime, imagePath, mediaType) {
    const modal = document.createElement('div');
    modal.classList.add('modal');
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <h2>Edit Post</h2>
            <label for="edit-content">Content:</label>
            <textarea id="edit-content" style="width: 100%; height: 100px;">${tweet}</textarea>
            <label for="edit-image">Image Path:</label>
            <input type="text" id="edit-image" value="${imagePath || ''}" style="width: 100%;">
            <label for="edit-date">Date:</label>
            <input type="date" id="edit-date" value="${postDate}">
            <label for="edit-time">Time:</label>
            <input type="time" id="edit-time" value="${postTime}">
            ${imagePath ? `<img src="${imagePath}" alt="Post Image" style="max-width: 200px; max-height: 200px;">` : ''}
             <p><strong>Output Type:</strong> ${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)}</p>
            <div style="display: flex; justify-content: flex-end; margin-top: 10px;">
                <button id="save-edit-button">Save</button>
                <button id="delete-post-button">Delete</button>
                <button id="cancel-edit-button">Cancel</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.close-button');
    closeButton.onclick = () => {
        document.body.removeChild(modal);
    };

    const saveButton = modal.querySelector('#save-edit-button');
    saveButton.onclick = () => {
        const newContent = document.getElementById('edit-content').value;
        const newDate = document.getElementById('edit-date').value;
        const newTime = document.getElementById('edit-time').value;

        fetch('/update_post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: postId,
                updated_post: {
                    content: newContent,
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
                loadScheduledPostsJS();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the post.');
        });
        document.body.removeChild(modal);
    };

    const cancelButton = modal.querySelector('#cancel-edit-button');
    cancelButton.onclick = () => {
        document.body.removeChild(modal);
    };

    const deleteButton = modal.querySelector('#delete-post-button');
    deleteButton.onclick = () => {
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
            document.body.removeChild(modal);
        }
    };
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

function edit(post_id) {
  document.querySelector(`#edit-${post_id}`).style.display = "block";
}

function update(post_id) {
  let newbody = document.querySelector(`#form-${post_id}`).value;

  // POST Method
  fetch(`/post/${post_id}`, {
    method: "POST",
    body: JSON.stringify({
      body: newbody,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      // Print result
      console.log(result);
    });

  document.querySelector(`#body-${post_id}`).innerHTML = newbody;
  document.querySelector(`#edit-${post_id}`).style.display = "none";
  return false;
}

function like(like_id) {
  let likeBtn = document.querySelector(`#like-btn-${like_id}`);
  let likeCount = document.querySelector(`#like-count-${like_id}`);

  // GET Method
  fetch(`/like_post/${like_id}`)
    .then((response) => response.json())
    .then((post) => {
      console.log(post);

      let count = post.likes;

      if (likeBtn.style.color === "black") {
        // Add like on the post
        fetch(`/like_post/${like_id}`, {
          method: "PUT",
          body: JSON.stringify({
            likes: true,
          }),
        });

        likeBtn.style.color = "red";
        likeCount.innerHTML = ++count;
      } else {
        // Remove like from the post
        fetch(`/like_post/${like_id}`, {
          method: "PUT",
          body: JSON.stringify({
            likes: false,
          }),
        });

        likeBtn.style.color = "black";
        likeCount.innerHTML = --count;
      }
    });
}

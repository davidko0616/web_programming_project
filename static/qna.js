    const postsContainer = document.getElementById("postsContainer");
    const searchInput = document.getElementById("searchInput");

    function savePosts(posts) {
      localStorage.setItem("qnaPosts", JSON.stringify(posts));
    }

    function loadPosts() {
      const posts = JSON.parse(localStorage.getItem("qnaPosts") || "[]");
      const keyword = searchInput.value.toLowerCase();
      postsContainer.innerHTML = "";

      posts.forEach((post, index) => {
        if (
          post.title.toLowerCase().includes(keyword) ||
          post.content.toLowerCase().includes(keyword) ||
          post.author.toLowerCase().includes(keyword)
        ) {
          const postEl = document.createElement("div");
          postEl.className = "post";

          // 댓글 초기화
          post.comments = post.comments || [];

          postEl.innerHTML = `
            <div class="title">${post.title}</div>
            <div class="meta">작성자: ${post.author} | ${post.timestamp}</div>
            <div class="body">${post.content}</div>
            <div class="actions">
              <button onclick="editPost(${index})">수정</button>
              <button onclick="deletePost(${index})">삭제</button>
            </div>
            <div class="comments" id="comments-${index}">
              ${post.comments.map(c => `<div class="comment">${c}</div>`).join("")}
              <div class="comment-input">
                <input type="text" id="commentInput-${index}" placeholder="댓글 입력..." />
                <button onclick="addComment(${index})">댓글 등록</button>
              </div>
            </div>
          `;

          postsContainer.appendChild(postEl);
        }
      });
    }

    function deletePost(index) {
      if (confirm("정말 삭제하시겠습니까?")) {
        const posts = JSON.parse(localStorage.getItem("qnaPosts") || "[]");
        posts.splice(index, 1);
        savePosts(posts);
        loadPosts();
      }
    }

    function editPost(index) {
      const posts = JSON.parse(localStorage.getItem("qnaPosts") || "[]");
      const newTitle = prompt("새 제목을 입력하세요", posts[index].title);
      const newContent = prompt("새 내용을 입력하세요", posts[index].content);
      if (newTitle && newContent) {
        posts[index].title = newTitle;
        posts[index].content = newContent;
        savePosts(posts);
        loadPosts();
      }
    }

    function addComment(index) {
      const input = document.getElementById(`commentInput-${index}`);
      const comment = input.value.trim();
      if (!comment) return;

      const posts = JSON.parse(localStorage.getItem("qnaPosts") || "[]");
      posts[index].comments = posts[index].comments || [];
      posts[index].comments.push(comment);
      savePosts(posts);
      loadPosts();
    }

    searchInput.addEventListener("input", loadPosts);
    window.addEventListener("load", loadPosts);
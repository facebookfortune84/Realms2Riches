import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Blog() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/blog/posts`)
      .then(res => res.json())
      .then(data => setPosts(data))
      .catch(err => console.error("Failed to load blog posts", err));
  }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold mb-8">Latest Updates</h2>
      <div className="space-y-8">
        {posts.length === 0 ? <p>No posts yet.</p> : posts.map(post => (
            <div key={post.slug} className="border-b border-gray-800 pb-8">
                <Link to={`/blog/${post.slug}`} className="block group">
                    <h3 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">{post.title}</h3>
                    <div className="text-gray-500 text-sm mb-4">{post.date}</div>
                    <p className="text-gray-300">{post.summary}</p>
                </Link>
            </div>
        ))}
      </div>
    </div>
  );
}

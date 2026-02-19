import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function BlogPost() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/blog/posts/${slug}`)
      .then(res => res.json())
      .then(data => setPost(data))
      .catch(err => console.error("Failed to load post", err));
  }, [slug]);
  
  if (!post) return <div className="text-center py-10">Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto py-10">
      <Link to="/blog" className="text-primary hover:underline mb-8 display-block">&larr; Back to Blog</Link>
      <h1 className="text-4xl font-bold mb-4">{post.meta.title}</h1>
      <div className="text-gray-500 mb-8">{post.meta.date}</div>
      <div className="prose prose-invert max-w-none whitespace-pre-wrap">
        {post.content}
      </div>
    </div>
  );
}

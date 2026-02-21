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
  
  if (!post) return <div className="text-center py-20 font-mono animate-pulse text-gray-500">Retrieving Transmission...</div>;

  const title = post.meta?.title || post.meta?.Title || "Intelligence Report";
  const date = post.meta?.date || post.meta?.Date || "2026-02-20";

  return (
    <div className="max-w-3xl mx-auto py-20 px-4 font-mono">
      <Link to="/blog" className="text-primary hover:text-white mb-12 inline-block text-xs uppercase tracking-widest font-black">&larr; Back to Reports</Link>
      
      <div className="mb-16">
        <div className="text-primary text-[10px] uppercase font-black mb-4 tracking-[0.2em]">{date}</div>
        <h1 className="text-5xl font-black mb-8 tracking-tighter uppercase italic text-white leading-tight">{title}</h1>
        <div className="h-1 w-20 bg-primary/20"></div>
      </div>

      <div className="prose prose-invert max-w-none whitespace-pre-wrap text-gray-400 leading-relaxed text-lg selection:bg-primary selection:text-black">
        {post.content}
      </div>
    </div>
  );
}

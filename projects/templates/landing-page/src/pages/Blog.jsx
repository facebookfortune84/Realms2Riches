import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Blog() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const headers = { 
        'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || 'mock_dev_key',
        'ngrok-skip-browser-warning': 'true'
    };
    fetch(`${BACKEND_URL}/api/blog/posts`, { headers })
      .then(res => res.json())
      .then(data => setPosts(data))
      .catch(err => console.error("Blog Load Error:", err));
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-20 px-4 font-mono">
      <h2 className="text-5xl font-black mb-16 tracking-tighter uppercase italic text-white text-center">Intelligence <span className="text-primary">Reports</span></h2>
      <div className="grid gap-12">
        {posts.length === 0 ? <p className="text-center text-gray-600">No transmissions found.</p> : posts.map(post => (
            <Link key={post.slug} to={`/blog/${post.slug}`} className="group bg-black border-2 border-white/5 p-8 rounded-3xl hover:border-primary/20 transition-all">
                <div className="flex justify-between items-start mb-4">
                    <h3 className="text-2xl font-bold text-white group-hover:text-primary transition-colors">{post.title}</h3>
                    <span className="text-gray-600 text-[10px] uppercase font-bold">{post.date}</span>
                </div>
                <p className="text-gray-400 text-sm">{post.summary}</p>
            </Link>
        ))}
      </div>
    </div>
  );
}

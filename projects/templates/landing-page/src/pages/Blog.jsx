import { Link } from 'react-router-dom';

const posts = [
  { slug: "welcome", title: "Welcome to Realms to Riches", date: "2026-02-18", preview: "The future of software development is agentic." },
  { slug: "groq-speed", title: "Why We Switched to Groq", date: "2026-02-15", preview: "Latency matters when you're talking to a swarm." },
];

export default function Blog() {
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold mb-8">Latest Updates</h2>
      <div className="space-y-8">
        {posts.map(post => (
            <div key={post.slug} className="border-b border-gray-800 pb-8">
                <Link to={`/blog/${post.slug}`} className="block group">
                    <h3 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">{post.title}</h3>
                    <div className="text-gray-500 text-sm mb-4">{post.date}</div>
                    <p className="text-gray-300">{post.preview}</p>
                </Link>
            </div>
        ))}
      </div>
    </div>
  );
}

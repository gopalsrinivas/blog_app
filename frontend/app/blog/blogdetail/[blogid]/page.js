'use client';
import SeoMeta from "@layouts/partials/SeoMeta";
import axios from "axios";
import Link from "next/link";
import { useEffect, useState } from "react";

const Blogdetails = ({ params }) => {
    const { blogid } = params;
    const [blog, setBlog] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (blogid) {
            fetchBlog();
        }
    }, [blogid]);

    const fetchBlog = async () => {
        try {
            const response = await axios.get(`${process.env.API_URL}/api/blog/${blogid}`);
            if (response.data.status_code === 200) {
                setBlog(response.data.data);
            } else {
                throw new Error(response.data.message);
            }
        } catch (err) {
            setError(err.message || 'Failed to load the blog.');
        } finally {
            setLoading(false);
        }
    };

    // Loading and Error Messages
    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <p>Loading...</p>
            </div>
        );
    }
    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <p>{error}</p>
            </div>
        );
    }

    return (
        <section className="section">
            <SeoMeta title="Blog Detail" />
            {blog ? (
                <div className="container">
                    <article className="text-center">
                        <h1 className="h3">{blog.blog_title}</h1>
                        <ul className="mb-8 mt-4 flex flex-wrap items-center justify-center space-x-3 text-text">
                            <li>
                                <Link className="flex items-center hover:text-primary" href={`/authors/${blog.author_id}`}>
                                    <img
                                        alt="Mark Dinn"
                                        loading="lazy"
                                        width="50"
                                        height="50"
                                        decoding="async"
                                        className="mr-2 h-6 w-6 rounded-full"
                                        src="/_next/image?url=%2Fimages%2Fauthors%2Fmark-dinn.jpg&amp;w=128&amp;q=75"
                                    />
                                    <span>{blog.author_name}</span>
                                </Link>
                            </li>
                            <li>
                                {blog.updated_on
                                    ? new Date(blog.updated_on).toLocaleDateString()
                                    : new Date(blog.created_on).toLocaleDateString()}
                            </li>
                            <li>
                                <ul>
                                    <li className="inline-block">
                                        <Link className="mr-3 hover:text-primary" href={`/categories/${blog.category_id}`}>
                                            {blog.category_name}
                                        </Link>
                                        <Link className="mr-3 hover:text-primary" href={`/subcategories/${blog.subcategory_id}`}>
                                            {blog.subcategory_name}
                                        </Link>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                        <img
                            alt={blog.blog_title}
                            loading="lazy"
                            width="1000"
                            height="500"
                            decoding="async"
                            className="rounded-lg shadow-2xl"
                            src={blog.blog_image}
                        />
                        <div className="content mb-16 text-left">
                            <p>{blog.blog_content}</p>
                        </div>
                    </article>
                </div>
            ) : (
                <div className="flex items-center justify-center h-screen">
                    <p>Blog not found.</p>
                </div>
            )}
        </section>
    );
};

export default Blogdetails;

"use client";
import SeoMeta from "@layouts/partials/SeoMeta";
import axios from "axios";
import Link from "next/link";
import { useEffect, useState } from "react";

const BlogList = ({ params }) => {
    const { subcategoryid } = params;
    const [blogs, setBlogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalBlogs, setTotalBlogs] = useState(0);
    const [categoryName, setCategoryName] = useState('');
    const [subcategoryName, setSubcategoryName] = useState('');
    const itemsPerPage = 6;

    useEffect(() => {
        const fetchBlogs = async () => {
            setLoading(true);
            setError(null);

            if (subcategoryid) {
                try {
                    const { data } = await axios.get(
                        `${process.env.API_URL}/api/blog/subcategories/${subcategoryid}/blog?skip=${(currentPage - 1) * itemsPerPage}&limit=${itemsPerPage}`
                    );

                    // Check if data exists and assign
                    if (data) {
                        setBlogs(data.blogs || []);
                        setTotalBlogs(data.total_active_blogs || 0);
                        setCategoryName(data.category_name || '');
                        setSubcategoryName(data.subcategory_name || '');
                    }
                } catch (err) {
                    if (err.response && err.response.status === 404) {
                        setError("No blog details found for this subcategory.");
                    } else {
                        setError("Failed to load blogs.");
                    }
                } finally {
                    setLoading(false);
                }
            } else {
                setLoading(false);
                setError('No subcategories available.');
            }
        };

        fetchBlogs();
    }, [subcategoryid, currentPage]);

    const totalPages = Math.ceil(totalBlogs / itemsPerPage);

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage((prevPage) => prevPage + 1);
        }
    };

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage((prevPage) => prevPage - 1);
        }
    };

    // Function to format time ago
    const timeAgo = (date) => {
        const now = new Date();
        const seconds = Math.floor((now - new Date(date)) / 1000);
        let interval = Math.floor(seconds / 31536000);

        if (interval >= 1) return `${interval} year${interval === 1 ? '' : 's'} ago`;
        interval = Math.floor(seconds / 2592000);
        if (interval >= 1) return `${interval} month${interval === 1 ? '' : 's'} ago`;
        interval = Math.floor(seconds / 86400);
        if (interval >= 1) return `${interval} day${interval === 1 ? '' : 's'} ago`;
        interval = Math.floor(seconds / 3600);
        if (interval >= 1) return `${interval} hour${interval === 1 ? '' : 's'} ago`;
        interval = Math.floor(seconds / 60);
        if (interval >= 1) return `${interval} minute${interval === 1 ? '' : 's'} ago`;
        return `${seconds} seconds ago`;
    };

    if (loading) return <p className="text-center">Loading...</p>;

    if (error) return (
        <div className="flex items-center justify-center h-screen bg-gray-100">
            <div className="bg-white p-6 rounded-lg shadow-lg">
                <p className="text-lg font-semibold text-gray-700">{error}</p>
            </div>
        </div>
    );

    if (blogs.length === 0) return (
        <div className="flex items-center justify-center h-screen bg-gray-100">
            <div className="bg-white p-6 rounded-lg shadow-lg">
                <p className="text-lg font-semibold text-gray-700">No blogs available in this subcategory.</p>
            </div>
        </div>
    );

    return (
        <>
            <SeoMeta title="Blog List" />
            <div className="max-w-screen-xl mx-auto p-5 sm:p-10 md:p-16">
                <div className="border-b mb-5 flex justify-between text-sm">
                    <div className="text-indigo-600 flex items-center pb-2 pr-2 border-b-2 border-indigo-600 uppercase">
                        <svg
                            className="h-6 mr-3"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 455.005 455.005"
                        >
                            {/* SVG content here */}
                        </svg>
                        <p className="font-semibold inline-block">
                            {categoryName} &gt;&gt; {subcategoryName}
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10 mb-10">
                    {blogs.map((blog) => (
                        <article key={blog.id} className="rounded overflow-hidden shadow-lg flex flex-col">
                            <Link href={`/blog/blogdetail/${blog.id}`}>
                                <div className="relative">
                                    <img
                                        className="w-full"
                                        src={blog.image ? `http://localhost:8000/media/${blog.image.split('/').pop()}` : "https://via.placeholder.com/500"}
                                        alt={blog.title}
                                    />
                                    <div className="hover:bg-transparent transition duration-300 absolute bottom-0 top-0 right-0 left-0 bg-gray-900 opacity-25"></div>
                                </div>
                                <div className="text-xs absolute top-0 right-0 bg-indigo-600 px-4 py-2 text-white mt-3 mr-3 hover:bg-white hover:text-indigo-600 transition duration-500 ease-in-out">
                                    Cooking
                                </div>

                                <div className="px-6 py-4 mb-auto">
                                    <Link
                                        href={`/blog/${blog.id}`}
                                        className="font-medium text-lg inline-block hover:text-indigo-600 transition duration-500 ease-in-out mb-2"
                                    >
                                        {blog.title}
                                    </Link>
                                    <p className="text-gray-500 text-sm">
                                        {blog.content}
                                    </p>
                                </div>
                                <div className="px-6 py-3 flex flex-row items-center justify-between bg-gray-100">
                                    <Link href="#" className="py-1 text-xs font-regular text-gray-900 mr-1 flex flex-row items-center">
                                        <svg
                                            height="13px"
                                            width="13px"
                                            version="1.1"
                                            id="Layer_1"
                                            xmlns="http://www.w3.org/2000/svg"
                                            xmlnsXlink="http://www.w3.org/1999/xlink"
                                            x="0px"
                                            y="0px"
                                            viewBox="0 0 512 512"
                                            style={{ enableBackground: 'new 0 0 512 512' }}
                                            xmlSpace="preserve"
                                        >
                                            <g>
                                                <g>
                                                    <path d="M256,0C114.837,0,0,114.837,0,256s114.837,256,256,256s256-114.837,256-256S397.163,0,256,0z M277.333,256 c0,11.797-9.536,21.333-21.333,21.333h-85.333c-11.797,0-21.333-9.536-21.333-21.333s9.536-21.333,21.333-21.333h64v-128 c0-11.797,9.536-21.333,21.333-21.333s21.333,9.536,21.333,21.333V256z"></path>
                                                </g>
                                            </g>
                                        </svg>
                                        <span className="ml-1">{blog.updated_on ? timeAgo(blog.updated_on) : timeAgo(blog.created_on)}</span>
                                    </Link>
                                </div>
                            </Link>
                        </article>
                    ))}
                </div>

                <nav className="flex justify-center space-x-4 pt-3.5" aria-label="Pagination">
                    <button
                        onClick={handlePreviousPage}
                        disabled={currentPage === 1}
                        className={`rounded-lg border border-primary px-2 py-2 text-dark ${currentPage === 1 ? "bg-gray-300 cursor-not-allowed" : "bg-white hover:bg-primary hover:text-white"
                            }`}
                    >
                        <span className="sr-only">Previous</span>
                        <svg
                            className="mt-1 h-5 w-5"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            aria-hidden="true"
                        >
                            <path fillRule="evenodd" d="M6.293 9.293a1 1 0 011.414 0L10 11.586V4a1 1 0 112 0v7.586l2.293-2.293a1 1 0 011.414 1.414l-5 5a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                    <span className="self-center text-sm font-medium">{currentPage} of {totalPages}</span>
                    <button
                        onClick={handleNextPage}
                        disabled={currentPage === totalPages}
                        className={`rounded-lg border border-primary px-2 py-2 text-dark ${currentPage === totalPages ? "bg-gray-300 cursor-not-allowed" : "bg-white hover:bg-primary hover:text-white"
                            }`}
                    >
                        <span className="sr-only">Next</span>
                        <svg
                            className="mt-1 h-5 w-5"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            aria-hidden="true"
                        >
                            <path fillRule="evenodd" d="M13.707 9.293a1 1 0 00-1.414 0L10 11.586V4a1 1 0 10-2 0v7.586l-2.293-2.293a1 1 0 00-1.414 1.414l5 5a1 1 0 001.414 0l5-5a1 1 0 000-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                </nav>
            </div>
        </>
    );
};

export default BlogList;

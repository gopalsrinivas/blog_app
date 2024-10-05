"use client";
import React, { useState } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ContactForm = () => {
    const initialFormData = {
        name: '',
        email: '',
        subject: '',
        message: '',
    };

    const [formData, setFormData] = useState(initialFormData);
    const [errors, setErrors] = useState({});
    const [contactFormError, setContactFormError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value,
        });

        // Clear the error message when the user starts typing in the field
        setErrors({ ...errors, [name]: '' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (isFormValid()) {
            try {
                setIsSubmitting(true);
                const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/notifications/send-contact-email/`, new URLSearchParams(formData));
                console.log('Submission successful', response.data);
                toast.success('Your message has been sent successfully!', { autoClose: 5000 });
                setFormData(initialFormData);
                setErrors({});
                setContactFormError('');
            } catch (error) {
                if (error.response && error.response.data.detail) {
                    const newErrors = error.response.data.detail.reduce((acc, curr) => {
                        acc[curr.loc[1]] = curr.msg;
                        return acc;
                    }, {});
                    setErrors(newErrors);
                } else {
                    setContactFormError('An error occurred while submitting the form.');
                }
            } finally {
                setIsSubmitting(false);
            }
        }
    };

    const isFormValid = () => {
        const newErrors = {};

        if (formData.name.trim() === '') {
            newErrors.name = 'Name is required';
        }

        if (formData.email.trim() === '') {
            newErrors.email = 'Email is required';
        } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
            newErrors.email = 'Invalid email format';
        }

        if (formData.subject.trim() === '') {
            newErrors.subject = 'Subject is required';
        }

        if (formData.message.trim() === '') {
            newErrors.message = 'Message is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    return (
        <>
            <ToastContainer />
            <div className="p-4 mx-auto max-w-xl bg-white font-[sans-serif]">
                <h1 className="text-3xl text-gray-800 font-extrabold text-center">Contact us</h1>
                <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
                    {contactFormError && <p className="text-danger">{contactFormError}</p>}
                    <input
                        type="text"
                        name="name"
                        placeholder="Name"
                        className={`w-full rounded-md py-3 px-4 text-gray-800 bg-gray-100 ${errors.name ? 'border-red-500' : ''}`}
                        value={formData.name}
                        onChange={handleChange}
                    />
                    {errors.name && <p className="text-red-700">{errors.name}</p>}

                    <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        className={`w-full rounded-md py-3 px-4 text-gray-800 bg-gray-100 ${errors.email ? 'border-red-500' : ''}`}
                        value={formData.email}
                        onChange={handleChange}
                    />
                    {errors.email && <p className="text-red-700">{errors.email}</p>}

                    <input
                        type="text"
                        name="subject"
                        placeholder="Subject"
                        className={`w-full rounded-md py-3 px-4 text-gray-800 bg-gray-100 ${errors.subject ? 'border-red-500' : ''}`}
                        value={formData.subject}
                        onChange={handleChange}
                    />
                    {errors.subject && <p className="text-red-700">{errors.subject}</p>}

                    <textarea
                        name="message"
                        rows="6"
                        placeholder="Message"
                        className={`w-full rounded-md px-4 text-gray-800 bg-gray-100 ${errors.message ? 'border-red-500' : ''}`}
                        value={formData.message}
                        onChange={handleChange}
                    ></textarea>
                    {errors.message && <p className="text-red-700">{errors.message}</p>}

                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="text-white bg-blue-500 hover:bg-blue-600 tracking-wide rounded-md text-sm px-4 py-3 w-full"
                    >
                        {isSubmitting ? 'Sending...' : 'Send'}
                    </button>
                </form>
            </div>
        </>
    );
};

export default ContactForm;

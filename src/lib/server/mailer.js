import nodemailer from 'nodemailer';
import { env } from '$env/dynamic/private';

export function getTransporter()
{
    return nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: env.GMAIL_USER,
            pass: env.GMAIL_PASS
        }
    });
}

export async function sendEmail({ to, subject, html })
{
    const transporter = getTransporter();
    return transporter.sendMail({
        from: `Mouse Acceleration Study <${env.GMAIL_USER}>`,
        to,
        subject,
        html
    });
}

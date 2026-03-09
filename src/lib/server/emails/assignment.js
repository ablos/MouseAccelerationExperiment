export function assignmentEmail(name, code, group)
{
    const firstName = name ? name.split(' ')[0].charAt(0).toUpperCase() + name.split(' ')[0].slice(1).toLowerCase() : 'there';
    const isExperimental = group === 'experimental';

    const bodyText = isExperimental
        ? `You have been assigned to the <strong>experimental group</strong>. This means you will need to change your mouse acceleration settings before your next session. Please follow the tutorial for your operating system using the links below.`
        : `You have been assigned to the <strong>control group</strong>. This means you do not need to change any settings — simply continue using your mouse as normal for all remaining sessions.`;

    const tutorialSection = isExperimental ? `
        <!-- Tutorial links -->
        <div style="background:#f4f4f5;border-radius:8px;padding:24px;margin:0 0 24px;">
            <p style="margin:0 0 12px;color:#18181b;font-size:15px;font-weight:600;">Setup instructions</p>
            <p style="margin:0 0 16px;color:#52525b;font-size:14px;line-height:1.6;">
                Please follow the guide for your operating system <strong>before your next session</strong>.
                Once done, keep the setting active for all remaining sessions.
            </p>
            <table cellpadding="0" cellspacing="0" style="width:100%;">
                <tr>
                    <td style="padding-right:8px;">
                        <a href="https://experiment.ablos.nl/tutorials/windows.pdf"
                           style="display:block;text-align:center;background:#18181b;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:6px;font-size:14px;font-weight:500;">
                            Windows tutorial
                        </a>
                    </td>
                    <td style="padding-left:8px;">
                        <a href="https://experiment.ablos.nl/tutorials/macos.pdf"
                           style="display:block;text-align:center;background:#18181b;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:6px;font-size:14px;font-weight:500;">
                            macOS tutorial
                        </a>
                    </td>
                </tr>
            </table>
        </div>
    ` : '';

    return `
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f4f4f5;font-family:sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
                <tr><td align="center">
                <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">

                    <!-- Header -->
                    <tr><td style="background:#18181b;padding:32px;text-align:center;">
                    <span style="color:#ffffff;font-size:20px;font-weight:600;">Mouse Acceleration Study</span>
                    </td></tr>

                    <!-- Body -->
                    <tr><td style="padding:32px;">
                    <p style="margin:0 0 16px;color:#18181b;font-size:16px;">Hi ${firstName},</p>
                    <p style="margin:0 0 24px;color:#52525b;font-size:15px;line-height:1.6;">
                        Your baseline session has been reviewed and you have now been assigned to a group.
                    </p>
                    <p style="margin:0 0 24px;color:#52525b;font-size:15px;line-height:1.6;">
                        ${bodyText}
                    </p>

                    ${tutorialSection}

                    <!-- Code -->
                    <div style="background:#f4f4f5;border-radius:8px;padding:24px;text-align:center;margin:0 0 24px;">
                        <p style="margin:0 0 8px;color:#71717a;font-size:12px;text-transform:uppercase;letter-spacing:0.1em;">Your participant code</p>
                        <span style="font-family:monospace;font-size:36px;font-weight:700;color:#18181b;letter-spacing:0.15em;">${code}</span>
                    </div>

                    <p style="margin:0 0 24px;color:#52525b;font-size:15px;line-height:1.6;">
                        If you have any questions, do not reply to this email. Contact Abel at
                        <a href="mailto:a.dieterich@students.uu.nl?SUBJECT=Help Experiment" style="color:#18181b;">a.dieterich@students.uu.nl</a>.
                    </p>

                    <!-- CTA -->
                    <div style="text-align:center;">
                        <a href="https://experiment.ablos.nl" style="background:#18181b;color:#ffffff;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:15px;font-weight:500;display:inline-block;">
                        Go to the study
                        </a>
                    </div>
                    </td></tr>

                    <!-- Footer -->
                    <tr><td style="padding:16px 32px;border-top:1px solid #f4f4f5;text-align:center;">
                    <p style="margin:0;color:#a1a1aa;font-size:12px;">
                        This message was sent by students at Utrecht University.
                    </p>
                    </td></tr>

                </table>
                </td></tr>
            </table>
        </body>
        </html>
    `;
}

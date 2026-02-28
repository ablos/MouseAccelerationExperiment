<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import { page } from '$app/stores';
    import { LayoutDashboard, Users } from 'lucide-svelte';
    
    let { children } = $props();
</script>

{#snippet navItem(href, icon, label)}
    {@const Icon = icon}
    
    <a href={href} class="flex items-center gap-2 px-3 py-2 rounded text-sm 
    {
        $page.url.pathname === href || (href !== '/dashboard' && $page.url.pathname.startsWith(href)) ?
        'bg-zinc-800 text-zinc-100' :
        'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800'
    }">
        <Icon size={16} />
        {label}
    </a>
{/snippet}

<div class="flex h-screen w-full">
    <div class="flex flex-col w-65 border-r border-zinc-700 px-2 py-5">
        <!-- Logo -->
        <img src='/img/logo.png' alt='' class='w-1/2 aspect-square object-contain mx-auto mb-2' />
        <span class="mx-auto font-mono">The Pointer Brothers</span>
        
        <hr class='my-4 w-4/5 mx-auto border-zinc-700' />
        
        <!-- Nav buttons -->
        {@render navItem('/dashboard', LayoutDashboard, 'Overview')}
        {@render navItem('/dashboard/participants', Users, 'Participants')}
        
        <!-- Logout button -->
        <form method="POST" action="/dashboard?/logout" class="mt-auto">
            <Button type="submit" class="w-full cursor-pointer">
                Log Out
            </Button>
        </form>
    </div>
    
    <div class="flex flex-1 overflow-y-auto">
        {@render children()}
    </div>
</div>
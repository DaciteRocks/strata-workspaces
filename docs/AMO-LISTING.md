# Strata Workspaces — addons.mozilla.org listing draft

Paste-ready text for the AMO submission form. Choose **"On this site"** (listed) when uploading.

## Upload

| Field | Value |
| - | - |
| Package | `addon/dist-zip/strata-workspaces@dacite.dev-v6.0.0.1-prod.zip` from `npm run build-zip` |
| Source code | `addon/dist-zip/strata-workspaces@dacite.dev-v6.0.0.1-dev.zip` — answer **Yes** to "Do you need to submit source code?" (webpack) |
| Compatibility | Firefox for desktop only (not Android), 142.0 and later |

## Describe

**Name:** Strata Workspaces

**Add-on URL slug:** `strata-workspaces`

**Summary** (max 250 characters, this one is 205):

> Vivaldi-style workspaces for your tabs: switch the whole tab bar between named workspaces, keep Firefox tab groups inside each one, restore them after a restart, and keep just one tab group open at a time.

**Description:**

> Strata Workspaces brings Vivaldi-style workspaces and tab stacks to Firefox.
>
> **Workspaces**
> - Keep separate, named sets of tabs and switch the whole tab bar between them in one click, from the
>   toolbar popup, the sidebar or a hotkey.
> - Tabs of other workspaces are hidden, not closed, so switching is instant.
>
> **Firefox tab groups inside each workspace**
> - Use Firefox's own tab groups inside a workspace. Each workspace remembers its tab groups, with their
>   names, colors and which tabs belong to them.
> - Tab groups never leak into other workspaces, and they come back grouped after a browser restart.
>
> **One tab group open at a time**
> - Opening a tab group automatically collapses the one that was open, like Vivaldi's tab stacks.
> - Selecting a tab on the top bar (an ungrouped or pinned tab, or the tab shown beside a collapsed tab
>   group's header) collapses the open tab group, so the lower row disappears, as in Vivaldi.
> - Tab groups are only ever collapsed automatically, never opened: you open a tab group from its header.
> - Both rules can be turned off in Settings ("Keep only one native tab group expanded at a time (Vivaldi-style)").
> - Optional: the project's `userChrome.css` shows the open tab group on its own second row under the tab
>   bar. Instructions are in the source repository.
>
> **Also included**
> - Containers per workspace, archive, bookmarks export and backups.
>
> **Privacy:** collects nothing and sends nothing. No analytics, no accounts, no developer server.
>
> **Credits:** based on Simple Tab Groups by Drive4ik, licensed under the Mozilla Public License 2.0.
> Source code: https://github.com/DaciteRocks/strata-workspaces
>
> **Known limitations:** selecting a tab inside a collapsed tab group does not open that tab group (this
> is Firefox's own behavior); open it from its header. Some non-English translations still say "STG".
> Simple Tab Groups' cloud sync is switched off, and its plugins and Windows backup helper do not work
> with this add-on. Do not run it together with Simple Tab Groups.

**Categories:** Tabs

**Support email:** leave empty, or use an address you want to publish.

**Support website:** https://github.com/DaciteRocks/strata-workspaces/issues

**License:** Mozilla Public License 2.0

**Privacy policy:** optional, since the add-on collects no data. Pasting `docs/PRIVACY.md` is still
recommended so users can see that.

## Additional details

**Homepage:** https://github.com/DaciteRocks/strata-workspaces

**Tags** (pick from AMO's list): tabs, productivity, tab management

## Images

**Icon:** AMO does not read the manifest icon; until one is uploaded the listing shows its default
puzzle piece. Upload `docs/amo/icon-128.png` in Developer Hub → the add-on → Edit Listing → Images →
Add-on icon (PNG or JPG, square, at least 128 px, not animated; AMO resizes it to 32/64/128). After any
change to `addon/src/icons/icon.svg`, regenerate it with `npm run icons` from `addon/` (needs Firefox and
Python with Pillow); `docs/amo/icon-preview.png` shows the result at 16–128 px.

**Screenshots:** the current captures live in `docs/amo/screenshots/`. AMO can require at least 1000×750
at exactly 4:3 and shows thumbnails boxed to 533×400, so full-window 4:3 captures (1280×960 or 1600×1200)
display best; the four tab-bar strips there are below that and may be refused.

To take in Firefox with the add-on installed, one feature each:

1. The toolbar popup listing several workspaces.
2. The tab bar with two Firefox tab groups, one open and one collapsed.
3. The same window after switching to another workspace, showing its own tabs and tab groups.
4. The `userChrome.css` two-row look, with the open tab group on the second row.
5. The Settings page section with "Keep only one native tab group expanded at a time (Vivaldi-style)".

## Version notes (6.0.0.1)

> First release of Strata Workspaces:
> - Workspaces: named sets of tabs, switched in one click, with Firefox tab groups that are kept per
>   workspace and come back after a restart.
> - One tab group open at a time: opening a tab group collapses the one that was open.
> - Selecting a tab on the top bar collapses the open tab group, so the lower row disappears.
>
> Compared with Simple Tab Groups, its groups are called workspaces here.

## Notes to reviewer

> This is a fork of Simple Tab Groups (MPL-2.0) with a new name, icon and add-on id, plus a module that
> keeps at most one native tab group expanded per window and collapses it when a tab outside it is
> selected (`src/js/groups-native-exclusive.js`). Upstream's GitHub
> Gist cloud sync is disabled by `CLOUD_SYNC_AVAILABLE = false` in `src/js/constants.js`; its code is kept
> for merges but its UI, hotkey, menu item and background alarm are off.
>
> Build instructions are in the source archive's README.md: `npm ci` then `npm run build-for-amo`, output
> in `dist/`. No minification.
>
> Data collection: `required: ["none"]`. The add-on makes no network requests of its own; the plugin
> icons on the About page and the conflicting add-on icons use a local generic icon instead of
> addons.mozilla.org.
>
> Permissions: `tabs`, `tabHide`, `tabGroups`, `sessions` manage and hide workspace tabs and their tab groups;
> `contextualIdentities`, `cookies`, `webRequest`, `webRequestBlocking`, `<all_urls>` reopen a tab in its
> workspace's container; the content script on all pages listens for the add-on's own hotkeys and draws its in-page workspace picker
> and prompt dialogs;
> `menus`, `notifications`, `alarms` for context menus, messages and scheduled backups; `downloads` saves
> backup files; `management` detects conflicting tab add-ons; `storage`, `unlimitedStorage` store
> workspaces. Optional: `bookmarks` for bookmark export, `nativeMessaging` for the local backup helper,
> `browserSettings` for new-tab settings.
>
> Validator: the one remaining warning, "Unsafe assignment to innerHTML" in `js/vue.runtime.esm.js`, is the
> unmodified Vue 2.7.16 runtime's `v-html` implementation. Every `v-html` binding in the add-on receives its own
> locale strings with hard-coded URLs and values, never page or user content. The other three warnings from the
> previous validator run are fixed in this version: `strict_min_version` is now 142.0 (the Android-min-version
> warning; the add-on is desktop only), the dynamic `import()` in `js/module-runner.js` is a static module map,
> and `createContextualFragment` in `js/lang.js` is replaced by `DOMParser` (both taken unchanged from
> upstream Simple Tab Groups). `npm run lint:amo` runs `web-ext lint` on `dist/`.

package cctv.cse.com.cctv_client;

/**
 * Created by sy081 on 2018-09-14.
 */

public class Item {
    private String content;
    private String title;
    private boolean active;

    public Item(String content, boolean active) {
        this.content = content;
        this.active = active;
    }

    public void setTitle(String title) { this.title = title; }

    public String getTitle() { return title; }

    public String getContent() {
        return content;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }
}

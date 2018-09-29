package cctv.cse.com.cctv_client.window;

import android.content.Context;
import android.graphics.drawable.ColorDrawable;
import android.os.Handler;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.PopupWindow;
import android.widget.TextView;

import java.util.List;

import cctv.cse.com.cctv_client.R;
import cctv.cse.com.cctv_client.adapter.RecyclerPopupWindowAdapter;
import cctv.cse.com.cctv_client.etc.Item;

/**
 * Created by sy081 on 2018-09-14.
 * Recycler custom view
 */

public class RecyclerPopupWindow extends PopupWindow implements RecyclerPopupWindowAdapter.OnItemClickListener, PopupWindow.OnDismissListener {
    private List<Item> items;
    private PopupWindow popupWindow;
    private RecyclerView recyclerView;
    private TextView titleTextview;
    private RecyclerPopupWindowAdapter recyclerPopupWindowAdapter;
    private CallBack mCallBack;
    private int position;
    private int prePosition;
    private boolean isClickItem;


    /**
     * RecyclerPopupWindow Constructor
     * If item i is active, set i to previous position
     */
    public RecyclerPopupWindow(List<Item> items) {
        this.items = items;
        for (int i = 1; i < items.size(); ++i) {
            if (items.get(i).isActive()) {
                prePosition = i;
                break;
            }
        }
    }

    /**
     * Show popup window with down in and out animation
     *
     */
    public void showPopupWindow(Context context, View anchor, int window_width, int window_height, int xoff, int yoff) {
        View contentView = LayoutInflater.from(context).inflate(R.layout.popup_window, null);
        popupWindow = new PopupWindow(contentView, window_width, window_height, true);
        popupWindow.setBackgroundDrawable(new ColorDrawable(0x00000000));

        // Make sure it goes out if you touch the outside of view.
        popupWindow.setOutsideTouchable(true);
        popupWindow.setOnDismissListener(this);

        // Set view according to id
        recyclerView = contentView.findViewById(R.id.rv_function_fire_time);
        titleTextview = contentView.findViewById(R.id.rv_title);

        recyclerView.setLayoutManager(new LinearLayoutManager(context));

        // Initialize RecyclerView Adapter
        recyclerPopupWindowAdapter = new RecyclerPopupWindowAdapter(items);
        recyclerPopupWindowAdapter.setOnItemClickListener(this);
        recyclerView.setAdapter(recyclerPopupWindowAdapter);

        // Set animation
        popupWindow.setAnimationStyle(R.style.Popwindow_Anim_Down);

        // Set drop down window's offset from anchor
        popupWindow.showAsDropDown(anchor, xoff, yoff);
    }

    /**
     * Callback function for getting item information
     */
    public void setCallBack(CallBack callBack) {
        mCallBack = callBack;
    }

    /**
     * If item is clicked, set position, isClickItem, and change position.
     */
    @Override
    public void onItemClick(int pos) {
        position = pos;
        isClickItem = true;
        changePos(true);
    }

    /**
     * This is function to change clicked item position
     * When the position is changed, the window is closed.
     */
    private void changePos(boolean isCloseWindow) {

        // If position and prePosition are different, set prePosition to inactive.
        if (position != prePosition) {
            items.get(prePosition).setActive(false);
            recyclerPopupWindowAdapter.notifyItemChanged(prePosition);
        }

        // Set position is active if it is not -1
        if (position >= 0) {
            items.get(position).setActive(true);
            recyclerPopupWindowAdapter.notifyItemChanged(position);
        }

        // Close window
        if (isCloseWindow) {
            (new Handler()).postDelayed(new Runnable() {
                @Override
                public void run() {
                    mCallBack.callback(items.get(position).getContent());
                    destroyPopWindow();
                }
            }, 450);
        }
    }

    /**
     * This is function to call back "-1", if none of items was clicked.
     */
    @Override
    public void onDismiss() {
        if (!isClickItem) {
            mCallBack.callback("-1");
        }
    }

    /**
     * This is function to destroy PopupView
     */
    private void destroyPopWindow() {
        if (popupWindow != null) {
            popupWindow.dismiss();
            popupWindow = null;
        }
    }

    /**
     * This is function to set RecyclerPopupView's title
     */
    public void setTitle(String title){
        titleTextview.setText(title);
    }

    /**
     * Callback interface to receive a string argument
     */
    public interface CallBack {
        void callback(String value);
    }
}
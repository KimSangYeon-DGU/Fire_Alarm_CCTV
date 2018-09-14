package cctv.cse.com.cctv_client;

import android.content.Context;
import android.graphics.drawable.ColorDrawable;
import android.os.Handler;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.PopupWindow;

import java.util.List;

/**
 * Created by sy081 on 2018-09-14.
 */

public class RecyclerPopupWindow extends PopupWindow implements RecyclerPopupWindowAdapter.OnItemClickListener, PopupWindow.OnDismissListener {
    private List<Item> items;
    private PopupWindow popupWindow;
    private RecyclerView recyclerView;
    private RecyclerPopupWindowAdapter recyclerPopupWindowAdapter;
    private CallBack mCallBack;
    private int position;
    private int prePosition;
    private boolean isClickItem;


    public RecyclerPopupWindow(List<Item> items) {
        this.items = items;
        for (int i = 1; i < items.size(); ++i) {
            if (items.get(i).isActive()) {
                prePosition = i;
                break;
            }
        }
    }

    public void showPopupWindow(Context context, View anchor, int window_width, int window_height) {
        View contentView = LayoutInflater.from(context).inflate(R.layout.popup_window, null);
        popupWindow = new PopupWindow(contentView, window_width, window_height, true);
        popupWindow.setBackgroundDrawable(new ColorDrawable(0x00000000));
        popupWindow.setOutsideTouchable(true);

        popupWindow.setOnDismissListener(this);
        recyclerView = (RecyclerView) contentView.findViewById(R.id.rv_function_wash_time);
        recyclerView.setLayoutManager(new LinearLayoutManager(context));
        recyclerPopupWindowAdapter = new RecyclerPopupWindowAdapter(items);
        recyclerPopupWindowAdapter.setOnItemClickListener(this);
        recyclerView.setAdapter(recyclerPopupWindowAdapter);

        popupWindow.setAnimationStyle(R.style.Popwindow_Anim_Down);
        popupWindow.showAsDropDown(anchor, 100, 0);
    }

    public void setCallBack(CallBack callBack) {
        mCallBack = callBack;
    }

    @Override
    public void onItemClick(int pos) {
        position = pos;
        isClickItem = true;
        changePos(true);
    }

    private void changePos(boolean isCloseWindow) {

        if (position != prePosition && prePosition != 0) {
            items.get(prePosition).setActive(false);
            recyclerPopupWindowAdapter.notifyItemChanged(prePosition);
        }

        if (position > 0) {
            items.get(position).setActive(true);
            recyclerPopupWindowAdapter.notifyItemChanged(position);
        }
        if (isCloseWindow) {
            (new Handler()).postDelayed(new Runnable() {
                @Override
                public void run() {
                    mCallBack.callback(items.get(position).getTitle());
                    destroyPopWindow();
                }
            }, 450);
        }
    }

    @Override
    public void onDismiss() {
        if (!isClickItem) {
            mCallBack.callback("-1");
        }
    }


    private void destroyPopWindow() {
        if (popupWindow != null) {
            popupWindow.dismiss();
            popupWindow = null;
        }
    }

    public interface CallBack {
        void callback(String value);
    }
}